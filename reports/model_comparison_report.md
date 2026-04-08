# Final Model Mega-Comparison Report

Generated natively on RTX 2050 (4GB VRAM) evaluating 1 distinct models.

## 1. Executive Setup
Models were gracefully handled using an Ephemeral loop (`ollama pull` -> `Test` -> `ollama rm`) resolving disk threshold bottlenecks natively.

## 2. Global Performance Metrics
| model     |   tps |   ttft |   latency |   peak_vram_mb |
|:----------|------:|-------:|----------:|---------------:|
| tinyllama | 49.05 |   1.08 |       2.6 |         1601.5 |

## 3. Average TPS by Category
| model     |   Chat & Generation |
|:----------|--------------------:|
| tinyllama |               49.05 |

## 4. Analysis & Conclusion
For an exact breakdown matching JSON validity via Python parsing, review the generated artifacts inside `results/phase2` locally. Dashboard integration scales dynamically.
