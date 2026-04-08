# Final Model Mega-Comparison Report

Generated natively on RTX 2050 (4GB VRAM) evaluating 11 distinct models.

## 1. Executive Setup
Models were gracefully handled using an Ephemeral loop (`ollama pull` -> `Test` -> `ollama rm`) resolving disk threshold bottlenecks natively.

## 2. Global Performance Metrics
| model                       |    tps |   ttft |   latency |   peak_vram_mb |
|:----------------------------|-------:|-------:|----------:|---------------:|
| deepseek-r1:1.5b            |  78.18 |   0.16 |      1.79 |         1693.5 |
| granite-code:3b             |  19.26 |   0.26 |      6.82 |         2951.5 |
| llama3.2:1b                 |  67.86 |   0.08 |      1.92 |         2281.5 |
| phi3:mini                   |  14.53 |   0.37 |      9.18 |         2973.5 |
| phi4-mini-reasoning         |  11.54 |   0.79 |     11.89 |         3591.5 |
| qwen2.5-coder:0.5b          | 126.66 |   0.09 |      1.11 |         1001.5 |
| qwen2.5-coder:0.5b-base     | 123.03 |   0.09 |      1.13 |         1127.5 |
| qwen2.5-coder:1.5b-instruct |  78.09 |   0.1  |      1.73 |         1693.5 |
| qwen2.5:1.5b-instruct       |  77.97 |   0.51 |      2.01 |         1695.5 |
| qwen2:1.5b-instruct         |  81.48 |   0.08 |      1.6  |         1643.5 |
| tinyllama                   |  67.8  |   0.82 |      2.22 |         1601.5 |

## 3. Average TPS by Category
| model                       |   Chat & Generation |   Coding Generation |   Medium Reasoning |
|:----------------------------|--------------------:|--------------------:|-------------------:|
| deepseek-r1:1.5b            |              nan    |              nan    |              78.18 |
| granite-code:3b             |              nan    |               19.26 |             nan    |
| llama3.2:1b                 |               67.86 |              nan    |             nan    |
| phi3:mini                   |               14.53 |              nan    |             nan    |
| phi4-mini-reasoning         |              nan    |              nan    |              11.54 |
| qwen2.5-coder:0.5b          |              nan    |              126.66 |             nan    |
| qwen2.5-coder:0.5b-base     |              nan    |              123.03 |             nan    |
| qwen2.5-coder:1.5b-instruct |              nan    |               78.09 |             nan    |
| qwen2.5:1.5b-instruct       |               77.97 |              nan    |             nan    |
| qwen2:1.5b-instruct         |               81.48 |              nan    |             nan    |
| tinyllama                   |               67.8  |              nan    |             nan    |

## 4. Analysis & Conclusion
For an exact breakdown matching JSON validity via Python parsing, review the generated artifacts inside `results/phase2` locally. Dashboard integration scales dynamically.
