#!/usr/bin/env python3
"""
Model Downloader Script
Downloads models from Ollama or HuggingFace based on model_commands.md

Usage:
    python scripts/download_models.py              # Download all
    python scripts/download_models.py --ollama     # Ollama only
    python scripts/download_models.py --hf         # HuggingFace only
    python scripts/download_models.py --list       # List available models
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MODEL_CONFIG, MODELS_DIR

console = Console()

def list_models():
    """List all available models."""
    table = Table(title="Available Models for Download")
    table.add_column("Category", style="cyan")
    table.add_column("Model Name", style="green")
    table.add_column("Source", style="yellow")
    table.add_column("Ollama Tag", style="magenta")
    
    for category, models in MODEL_CONFIG.items():
        for m in models:
            source = m["source"]
            ollama_tag = m.get("ollama_tag", "N/A")
            table.add_row(category, m["name"], source, ollama_tag)
    
    console.print(table)

def download_ollama_model(model_entry: dict) -> bool:
    """Download model from Ollama."""
    ollama_tag = model_entry.get("ollama_tag")
    if not ollama_tag:
        return False
    
    console.print(f"[cyan]Pulling from Ollama:[/cyan] {ollama_tag}")
    result = subprocess.run(["ollama", "pull", ollama_tag], capture_output=True, text=True)
    if result.returncode != 0:
        console.print(f"[red]Failed:[/red] {result.stderr}")
        return False
    console.print(f"[green]Success:[/green] {ollama_tag}")
    return True

def download_hf_model(model_entry: dict) -> bool:
    """Download model from HuggingFace."""
    hf_repo = model_entry.get("hf_repo")
    local_dir = model_entry.get("local_dir")
    
    if not hf_repo or not local_dir:
        return False
    
    model_path = Path(MODELS_DIR) / local_dir
    
    if model_path.exists() and any(model_path.iterdir()):
        console.print(f"[yellow]Already exists:[/yellow] {local_dir}")
        return True
    
    console.print(f"[cyan]Downloading from HuggingFace:[/cyan] {hf_repo}")
    result = subprocess.run(
        ["huggingface-cli", "download", hf_repo, "--local-dir", str(model_path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        console.print(f"[red]Failed:[/red] {result.stderr}")
        return False
    console.print(f"[green]Success:[/green] Downloaded to {model_path}")
    return True

def download_all(source_filter: str = None):
    """Download all models or filter by source."""
    total = 0
    success = 0
    
    for category, models in MODEL_CONFIG.items():
        console.print(f"\n[bold cyan]--- {category} ---[/bold cyan]")
        for m in models:
            source = m["source"]
            name = m["name"]
            
            if source_filter and source != source_filter:
                continue
            
            total += 1
            console.print(f"\n[{source}] {name}")
            
            if source == "ollama":
                if download_ollama_model(m):
                    success += 1
            elif source == "huggingface":
                if download_hf_model(m):
                    success += 1
    
    console.print(f"\n[bold green]Download Complete:[/bold green] {success}/{total} models")
    return success, total

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download AI models from Ollama or HuggingFace")
    parser.add_argument("--ollama", action="store_true", help="Download Ollama models only")
    parser.add_argument("--hf", action="store_true", help="Download HuggingFace models only")
    parser.add_argument("--list", action="store_true", help="List available models")
    
    args = parser.parse_args()
    
    if args.list:
        list_models()
    elif args.ollama:
        download_all("ollama")
    elif args.hf:
        download_all("huggingface")
    else:
        console.print("[bold green]Downloading ALL models...[/bold green]")
        download_all()
