import sys
import os
import shutil
import subprocess
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    os.environ['ANSI_COLORS_DISABLED'] = '1'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Force UTF-8 output on Windows
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import re
def strip_ansi(text):
    """Remove ANSI escape codes from text."""
    if text is None:
        return ""
    ansi_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_pattern.sub('', text)

def log(msg, end=None, flush=False):
    """Simple print wrapper with optional end parameter."""
    if end:
        print(msg, end=end, flush=flush)
    else:
        print(msg)
    sys.stdout.flush()

from src.benchmarker import Benchmarker
from src.structured_output import StructuredOutputTester
from src.model_comparator import ModelComparator
from config import MODEL_CONFIG, PROMPTS_DIR, RESULTS_DIR, TEMPS_TO_TEST, MODELS_DIR
from scripts.test_tracker import TestTracker

tracker = TestTracker()

def get_free_disk_space_gb() -> float:
    """Get free disk space in GB for the drive containing MODELS_DIR."""
    import shutil
    total, used, free = shutil.disk_usage(MODELS_DIR)
    return free / (1024 ** 3)

def clear_huggingface_cache():
    """Clear HuggingFace downloads from models directory to free disk space."""
    if os.path.exists(MODELS_DIR):
        for item in os.listdir(MODELS_DIR):
            item_path = os.path.join(MODELS_DIR, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    log(f"Cleared HuggingFace cache: {item}")
            except Exception as e:
                log(f"Warning: Could not clear {item}: {e}")

def check_disk_space(required_gb: float = 5.0) -> bool:
    """Check if sufficient disk space is available. Returns True if OK."""
    free_gb = get_free_disk_space_gb()
    if free_gb < required_gb:
        log(f"Low disk space: {free_gb:.2f} GB free (need {required_gb} GB)")
        log("Clearing HuggingFace cache...")
        clear_huggingface_cache()
        free_gb = get_free_disk_space_gb()
        log(f"After cleanup: {free_gb:.2f} GB free")
    if free_gb < required_gb:
        log(f"ERROR: Insufficient disk space ({free_gb:.2f} GB). Skipping model.")
        return False
    return True

def check_ollama_model_exists(model_tag: str) -> bool:
    """Check if model exists in Ollama."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, encoding='utf-8', errors='replace')
        return model_tag in result.stdout
    except:
        return False

def download_model(model_entry: dict) -> str:
    """
    Download model from Ollama or HuggingFace fallback.
    Returns the model tag/name to use for running.
    """
    ollama_tag = model_entry["ollama_tag"]
    source = model_entry.get("source", "ollama")
    
    if check_ollama_model_exists(ollama_tag):
        log(f"Model {ollama_tag} already exists")
        return ollama_tag
    
    if source == "ollama":
        log(f"Pulling {ollama_tag} from Ollama...")
        result = subprocess.run(["ollama", "pull", ollama_tag], capture_output=True, encoding='utf-8', errors='replace')
        if result.returncode == 0:
            log(f"Successfully downloaded {ollama_tag}")
        else:
            log(f"Pull output: {result.stdout[-500:] if len(result.stdout) > 500 else result.stdout}")
        
    elif source == "huggingface":
        hf_repo = model_entry.get("hf_repo")
        if not hf_repo:
            log(f"Missing hf_repo for {ollama_tag}")
            return None
        
        # Check disk space before HuggingFace download (typically 2-10 GB)
        if not check_disk_space(required_gb=5.0):
            return None
            
        log(f"Downloading {hf_repo} from HuggingFace...")
        local_dir = os.path.join(MODELS_DIR, ollama_tag.replace(':', '_'))
        result = subprocess.run(["python", "-m", "huggingface_hub.commands.huggingface_cli", "download", hf_repo, "--local-dir", local_dir, "--local-dir-use-symlinks", "False"], capture_output=True, encoding='utf-8', errors='replace')
        if result.returncode != 0:
            log(f"HuggingFace download error: {result.stderr[-500:] if len(result.stderr) > 500 else result.stderr}")
        
        # Identify the GGUF file
        gguf_files = [f for f in os.listdir(local_dir) if f.endswith('.gguf')]
        if not gguf_files:
            log(f"No GGUF file found in {hf_repo}")
            return None
        
        modelfile_path = os.path.join(local_dir, "Modelfile")
        with open(modelfile_path, "w") as f:
            f.write(f"FROM ./{gguf_files[0]}")
        
        log(f"Creating Ollama model from GGUF...")
        subprocess.run(["ollama", "create", ollama_tag, "-f", modelfile_path], encoding='utf-8', errors='replace')
    
    if check_ollama_model_exists(ollama_tag):
        log(f"Successfully loaded {ollama_tag}")
        return ollama_tag
    else:
        log(f"Failed to pull {ollama_tag} - model not found after engine resolution")
        return None

def cleanup_model(model_entry: dict, model_tag: str):
    """Remove model from Ollama and clear HuggingFace cache to reclaim disk space."""
    if model_tag:
        log(f"Removing {model_tag} from Ollama...")
        subprocess.run(["ollama", "rm", model_tag], capture_output=True)
        log(f"Reclaimed disk space from {model_tag}")
    
    # Clear HuggingFace downloads to free disk space
    source = model_entry.get("source", "ollama")
    if source == "huggingface":
        local_dir_name = model_tag.replace(':', '_') if model_tag else None
        if local_dir_name:
            local_dir = os.path.join(MODELS_DIR, local_dir_name)
            if os.path.exists(local_dir):
                try:
                    shutil.rmtree(local_dir)
                    log(f"Cleared HuggingFace cache: {local_dir_name}")
                except Exception as e:
                    log(f"Warning: Could not clear HF cache: {e}")
    
    # Show remaining disk space
    free_gb = get_free_disk_space_gb()
    log(f"Free disk space: {free_gb:.2f} GB")

def save_unified_result(results_list: list, model: str) -> str:
    """
    Saves the aggregated results of a model's run to a CSV formatted specifically for Phase 3 aggregation.
    Returns the path to the saved CSV file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_model = model.replace(":", "_").replace("/", "_")
    output_dir = os.path.join(RESULTS_DIR, "phase1")
    os.makedirs(output_dir, exist_ok=True)
    
    csv_path = os.path.join(output_dir, f"{safe_model}_MegaBench_{timestamp}.csv")
    df = pd.DataFrame(results_list)
    df.to_csv(csv_path, index=False)
    log(f"Saved results for '{model}' to {csv_path}")
    return csv_path

def load_existing_results(csv_path: str) -> list:
    """Load existing results from a CSV file to resume testing."""
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        return df.to_dict('records')
    return None

def run_project_pipeline():
    log("Starting Unified LLM Mega-Benchmark Pipeline with Checkpoint/Resume")
    log("=" * 60)
    
    prompts_path = os.path.join(PROMPTS_DIR, "benchmark_prompts.json")
    if not os.path.exists(prompts_path):
        log("prompts.json not found!")
        return
        
    with open(prompts_path, 'r') as f:
        all_prompts = json.load(f)
        
    benchmarker = Benchmarker()
    tester = StructuredOutputTester()
    
    total_models = sum(len(models) for models in MODEL_CONFIG.values())
    current_model_num = 0
    
    for category, model_configs in MODEL_CONFIG.items():
        cat_map = {"Coding": "Coding Generation", "Reasoning": "Medium Reasoning", "Chat": "Chat & Generation", "Multimodal/Vision": "Multimodal Vision"}
        target_category = cat_map[category]
        filtered_prompts = [p for p in all_prompts if p["category"] == target_category]
        
        for model_entry in model_configs:
            model_name = model_entry["name"]
            current_model_num += 1
            
            tracker.init_model(model_name, category)
            
            status, completed_prompts, total = tracker.get_model_progress(model_name)
            
            if status == "completed":
                log(f"\n[{current_model_num}/{total_models}] {model_name} ({category}) - Already completed, skipping")
                continue
            
            if status == "failed":
                log(f"\n[{current_model_num}/{total_models}] {model_name} ({category}) - Previously failed, skipping")
                log(f"  Error: {tracker.get_all_progress()['models'].get(model_name, {}).get('error', 'Unknown')}")
                continue
            
            log(f"\n[{current_model_num}/{total_models}] Evaluating {model_name} ({category})")
            log(f"  Status: {status}, Completed prompts: {completed_prompts}/{total}")
            
            model_tag = download_model(model_entry)
            if not model_tag:
                error_msg = "Download failed"
                log(f"  ERROR: {error_msg}")
                tracker.fail_model(model_name, error_msg)
                tracker.save_status_to_file()
                continue
            
            tracker.start_model(model_name)
            
            model_results = []
            start_index = 0
            
            if status == "in_progress" and completed_prompts > 0:
                existing_csv = tracker.get_all_progress()["models"].get(model_name, {}).get("csv_file")
                if existing_csv and os.path.exists(existing_csv):
                    existing_results = load_existing_results(existing_csv)
                    if existing_results:
                        model_results = existing_results
                        start_index = completed_prompts
                        log(f"  Resuming from prompt {start_index + 1}")
            
            log(f"  Running {len(filtered_prompts) - start_index} prompts...")
            
            import time
            loop_start_time = time.perf_counter()
            
            try:
                for i, p in enumerate(filtered_prompts):
                    if i < start_index:
                        continue
                    
                    # Calculate live ETA mapping
                    prompts_done = i - start_index
                    if prompts_done > 0:
                        elapsed = time.perf_counter() - loop_start_time
                        avg_time_per_prompt = elapsed / prompts_done
                        prompts_left = len(filtered_prompts) - i
                        eta_mins = (avg_time_per_prompt * prompts_left) / 60
                        log(f"  Prompt {i+1}/{len(filtered_prompts)} | Elapsed: {elapsed/60:.1f}m | ETA: {eta_mins:.1f}m", end="\r")
                    else:
                        log(f"  Prompt {i+1}/{len(filtered_prompts)} | Calculating ETA...", end="\r")
                    
                    unified_data = benchmarker.benchmark_single(model_tag, p)
                    
                    # PHASE 6 Optimization: Subsample Phase 2 structure logic to exactly the limit
                    from config import PHASE2_PROMPT_LIMIT
                    if i < (start_index + PHASE2_PROMPT_LIMIT):
                        for temp in TEMPS_TO_TEST:
                            temp_res = tester.generate_single_with_retry(model_tag, p["prompt"], category=target_category, temperature=temp)
                            unified_data[f"temp_{temp}_success"] = temp_res["success"]
                            unified_data[f"temp_{temp}_error"] = temp_res["error"]
                            unified_data[f"temp_{temp}_output"] = temp_res["output"]
                    
                    model_results.append(unified_data)
                    
                    tracker.update_checkpoint(model_name, i + 1)
                    
            except KeyboardInterrupt:
                log(f"\n  Interrupted! Saving checkpoint at prompt {len(model_results)}...")
                if model_results:
                    csv_path = save_unified_result(model_results, model_name)
                    tracker.update_checkpoint(model_name, len(model_results), csv_path)
                cleanup_model(model_entry, model_tag)
                tracker.save_status_to_file()
                log("  Checkpoint saved. Run again to resume.")
                return
            
            except Exception as e:
                error_msg = str(e)
                log(f"\n  ERROR during testing: {error_msg}")
                if model_results:
                    csv_path = save_unified_result(model_results, model_name)
                    tracker.update_checkpoint(model_name, len(model_results), csv_path)
                tracker.fail_model(model_name, error_msg)
                tracker.save_status_to_file()
                cleanup_model(model_entry, model_tag)
                continue
            
            log(f"\n  Testing complete! ({len(model_results)} prompts)")
            csv_path = save_unified_result(model_results, model_name)
            tracker.complete_model(model_name, csv_path)
            log(f"  Marked as completed")
            
            cleanup_model(model_entry, model_tag)
            
            tracker.save_status_to_file()
            log("  Status saved to TEST_STATUS.md")
            
            log("\n" + "-" * 60)
            log(tracker.generate_status_report())
    
    log("\n" + "=" * 60)
    log("ALL MODELS COMPLETED!")
    log("=" * 60)
    
    log("\nGenerating Final Report...")
    comparator = ModelComparator()
    comparator.run_offline_report()

if __name__ == "__main__":
    try:
        run_project_pipeline()
    except KeyboardInterrupt:
        log("\n\nPipeline interrupted. Run again to resume from last checkpoint.")
