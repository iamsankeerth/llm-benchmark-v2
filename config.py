import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# TEMPORARY: Single model for testing
MODEL_CONFIG = {
    "Chat": [
        {"name": "TinyLlama-1.1B", "ollama_tag": "tinyllama", "source": "ollama"},
    ]
}

# Backward compatibility
MODELS = {
    category: [m["ollama_tag"] for m in models]
    for category, models in MODEL_CONFIG.items()
}

# Execute Optimizations
BENCHMARK_RUNS = 1            
WARMUP_RUNS = 0               
# Step 1: Reduce Tokens to safely cap generation bandwidth while hitting logical structs
MAX_NEW_TOKENS = 128          
# Step 1: Drastically optimize total inferences to only check extremes
TEMPS_TO_TEST = [0.0, 0.7]    
# Step 1: Subsample Phase 2 test limits to drop runtimes dramatically (84% speedup)
PHASE2_PROMPT_LIMIT = 10      

GPU_INDEX = 0
