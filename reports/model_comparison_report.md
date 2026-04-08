# Final Model Mega-Comparison Report

Generated natively on RTX 2050 (4GB VRAM) evaluating 2 distinct models.

## 1. Executive Setup
Models were gracefully handled using an Ephemeral loop (`ollama pull` -> `Test` -> `ollama rm`) resolving disk threshold bottlenecks natively.

## 2. Global Performance Metrics
| model              |    tps |   ttft |   latency |   peak_vram_mb |
|:-------------------|-------:|-------:|----------:|---------------:|
| qwen2.5-coder:0.5b | 126.66 |   0.09 |      1.11 |         1001.5 |
| tinyllama          |  49.05 |   1.08 |      2.6  |         1601.5 |

## 3. Average TPS by Category
| model              |   Chat & Generation |   Coding Generation |
|:-------------------|--------------------:|--------------------:|
| qwen2.5-coder:0.5b |              nan    |              126.66 |
| tinyllama          |               49.05 |              nan    |

## 4. Analysis & Conclusion
For an exact breakdown matching JSON validity via Python parsing, review the generated artifacts inside `results/phase2` locally. Dashboard integration scales dynamically.
