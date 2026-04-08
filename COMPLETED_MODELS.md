# Completed Models Tracking

Last Updated: 2026-04-08 15:41

## Successfully Completed (2 models)

| Model | Category | Prompts | Duration | Avg TPS | Avg Latency | Peak VRAM | CSV File |
|-------|----------|---------|----------|---------|-------------|-----------|----------|
| starcoder2:3b | Coding | 50/50 | ~266 min | ~40 t/s | ~6.8s | 2513 MB | starcoder2_3b_MegaBench_20260407_111916.csv |
| TinyLlama-1.1B | Chat | 50/50 | ~2.5 min | ~119 t/s | ~2.2s | 1522 MB | TinyLlama-1.1B_MegaBench_20260408_154118.csv |

## In Progress (1 model)

| Model | Category | Progress | Started | Last Checkpoint |
|-------|----------|----------|---------|------------------|
| qwen2.5-coder:3b-base | Coding | 8/50 | 2026-04-07 11:12 | 2026-04-07 11:28 |

## Failed Models (4 models)

| Model | Category | Error | Reason |
|-------|----------|-------|--------|
| llama-3.2-1b-code-instruct | Coding | Download failed | Disk full |
| qwen2.5-coder:1.5b | Coding | Download failed | Disk full |
| qwen2.5-coder:3b | Coding | Download failed | Disk full |
| qwen3-coder:30b | Coding | Removed from config | Too large (30B) |
| qwen2.5-coder:32b | Coding | Removed from config | Too large (32B) |

## Pending Models

Models waiting to be tested (after config update to run all):

### Chat Category (from original config)
- qwen2.5:3b
- phi3:mini
- qwen2.5:1.5b
- qwen2:1.5b
- llama3.2:3b
- yi:6b
- stablelm2:1.6b

### Coding Category (from original config)
- granite-code:3b
- qwen2.5-coder:0.5b
- qwen2.5-coder:0.5b-base

### Reasoning Category (from original config)
- phi4-mini
- deepseek-r1:1.5b
- orca2:7b

### Vision Category (from original config)
- qwen2.5-vl:3b

---

## Performance Notes

**Best Performance (so far):**
- **Fastest TPS**: TinyLlama-1.1B (~119 t/s)
- **Lowest VRAM**: TinyLlama-1.1B (~1.5 GB)
- **Best for 4GB GPU**: TinyLlama-1.1B

**Recommendations:**
1. Continue with small models (<3B) for optimal 4GB VRAM fit
2. Run models sequentially with cleanup to manage disk space
3. HuggingFace downloads require ~5GB free disk space