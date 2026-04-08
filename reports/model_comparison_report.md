# Final Model Mega-Comparison Report

Generated natively on RTX 2050 (4GB VRAM) evaluating 5 distinct models.

## 1. Executive Setup
Models were gracefully handled using an Ephemeral loop (`ollama pull` -> `Test` -> `ollama rm`) resolving disk threshold bottlenecks natively.

## 2. Global Performance Metrics
| model                       |    tps |   ttft |   latency |   peak_vram_mb |
|:----------------------------|-------:|-------:|----------:|---------------:|
| llama3.2:1b                 |   0    |   0    |      0    |         131    |
| phi4-mini-reasoning         |   0    |   0    |      0    |        2653.5  |
| qwen2.5-coder:1.5b-instruct |   0    |   0    |      0    |        2533.5  |
| starcoder2:3b               |  56.33 |   0.14 |      0.94 |        2996.51 |
| tinyllama                   | 109.98 |   0.11 |      1.29 |        1523.5  |

## 3. Average TPS by Category
| model                       |   Chat & Generation |   Coding Generation |   Medium Reasoning |
|:----------------------------|--------------------:|--------------------:|-------------------:|
| llama3.2:1b                 |              nan    |                0    |                nan |
| phi4-mini-reasoning         |              nan    |              nan    |                  0 |
| qwen2.5-coder:1.5b-instruct |              nan    |                0    |                nan |
| starcoder2:3b               |              nan    |               56.33 |                nan |
| tinyllama                   |              109.98 |              nan    |                nan |

## 4. Analysis & Conclusion
For an exact breakdown matching JSON validity via Python parsing, review the generated artifacts inside `results/phase2` locally. Dashboard integration scales dynamically.
