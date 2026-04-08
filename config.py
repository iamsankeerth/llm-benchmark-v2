import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Running remaining small models sequentially
MODEL_CONFIG = {
    "Coding": [
        {"name": "qwen2.5-coder:0.5b-base", "ollama_tag": "qwen2.5-coder:0.5b", "source": "ollama"},
        {"name": "qwen2.5-coder:1.5b-instruct", "ollama_tag": "qwen2.5-coder:1.5b-instruct", "source": "ollama"},
        {"name": "granite-code:3b", "ollama_tag": "granite-code:3b", "source": "ollama"},
    ],
    "Reasoning": [
        {"name": "deepseek-r1:1.5b", "ollama_tag": "deepseek-r1:1.5b", "source": "ollama"},
        {"name": "phi4-mini-reasoning", "ollama_tag": "phi4-mini-reasoning", "source": "ollama"},
    ],
    "Chat": [
        {"name": "qwen2.5:1.5b-instruct", "ollama_tag": "qwen2.5:1.5b-instruct", "source": "ollama"},
        {"name": "qwen2:1.5b-instruct", "ollama_tag": "qwen2:1.5b-instruct", "source": "ollama"},
        {"name": "phi3:mini", "ollama_tag": "phi3:mini", "source": "ollama"},
        {"name": "tinyllama", "ollama_tag": "tinyllama", "source": "ollama"},
        {"name": "llama3.2:1b", "ollama_tag": "llama3.2:1b", "source": "ollama"},
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
TEMPS_TO_TEST = [0.0, 0.7, 1.0]    
# Step 1: Subsample Phase 2 test limits to drop runtimes dramatically (84% speedup)
PHASE2_PROMPT_LIMIT = 10      

GPU_INDEX = 0
