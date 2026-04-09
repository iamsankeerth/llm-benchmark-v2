# Compatible Models for RTX 2050 (4GB VRAM)

> **Generated**: 2026-04-09
> **System**: AMD Ryzen 5 5500H, NVIDIA GeForce RTX 2050 (4GB VRAM)
> **Source**: llmfit analysis

---

## 📊 Summary

| Category | Perfect Fit Models |
|----------|-------------------|
| Coding | 10 |
| Chat | 38 |
| Multimodal | 30 |
| Reasoning | 10 |
| Good Fit (MoE) | 12 |
| **Total** | **100** |

---

## 📝 CODING Models (10 models)

| Model | Size | TPS | Source |
|-------|------|-----|--------|
| Qwen/Qwen2.5-Coder-0.5B | 494M | 391.9 | HuggingFace |
| Qwen/Qwen2.5-Coder-0.5B-Instruct | 494M | 391.9 | HuggingFace |
| bigcode/gpt_bigcode-santacoder | 1.1B | 172.1 | HuggingFace |
| ShahriarFerdoush/llama-3.2-1b-code-instruct | 1.2B | 156.7 | HuggingFace |
| Qwen/Qwen2.5-Coder-1.5B-Instruct | 1.5B | 125.4 | Ollama, HF |
| Qwen/Qwen2.5-Coder-1.5B-Instruct-AWQ | 1.8B | 163.4 | HuggingFace |
| bigcode/starcoder2-3b | 3.0B | 63.9 | Ollama, HF |
| Qwen/Qwen2.5-Coder-3B | 3.1B | 62.7 | Ollama, HF |
| Qwen/Qwen2.5-Coder-3B-Instruct | 3.1B | 62.7 | Ollama, HF |
| ibm-granite/granite-3b-code-base-2k | 3.5B | 66.0 | Ollama, HF |

### Ollama Commands:
```bash
ollama pull qwen2.5-coder:0.5b
ollama pull qwen2.5-coder:0.5b-instruct
ollama pull qwen2.5-coder:1.5b-instruct
ollama pull qwen2.5-coder:3b
ollama pull qwen2.5-coder:3b-instruct
ollama pull starcoder2:3b
ollama pull granite-code:3b
```

---

## 💬 CHAT Models (90+ models)

### Small (<1B)

| Model | Size | TPS | Source |
|-------|------|-----|--------|
| Qwen/Qwen2.5-0.5B-Instruct | 494M | 391.9 | HuggingFace |
| Qwen/Qwen2-0.5B-Instruct | 494M | 391.9 | HuggingFace |
| Qwen/Qwen1.5-0.5B-Chat | 620M | 312.5 | HuggingFace |
| Qwen/Qwen3-0.6B | 752M | 257.6 | HuggingFace |
| Qwen/Qwen3-0.6B-FP8 | 752M | 257.6 | HuggingFace |
| Qwen/Qwen3.5-0.8B | 873M | 221.7 | HuggingFace |
| Qwen/Qwen3.5-0.8B-Base | 873M | 221.7 | HuggingFace |

### 1B-2B

| Model | Size | TPS | Source |
|-------|------|-----|--------|
| TinyLlama/TinyLlama-1.1B-Chat-v1.0 | 1.1B | 176.0 | Ollama, HF |
| meta-llama/Llama-3.2-1B-Instruct | 1.2B | 156.7 | Ollama, HF |
| Qwen/Qwen2.5-1.5B-Instruct | 1.5B | 125.4 | Ollama, HF |
| Qwen/Qwen2-1.5B-Instruct | 1.5B | 125.4 | Ollama, HF |
| Qwen/Qwen2.5-1.5B | 1.5B | 125.4 | HuggingFace |
| Qwen/Qwen2-1.5B | 1.5B | 125.4 | HuggingFace |
| stabilityai/stablelm-2-1_6b-chat | 1.6B | 117.7 | HuggingFace |
| Qwen/Qwen3-1.7B-Base | 1.7B | 112.5 | HuggingFace |
| Qwen/Qwen1.5-1.8B-Chat | 1.8B | 105.4 | HuggingFace |
| Qwen/Qwen1.5-1.8B | 1.8B | 105.4 | HuggingFace |

### 2B-4B

| Model | Size | TPS | Source |
|-------|------|-----|--------|
| Qwen/Qwen3-1.7B | 2.0B | 95.3 | HuggingFace |
| Qwen/Qwen3-1.7B-FP8 | 2.0B | 95.3 | HuggingFace |
| Qwen/Qwen3.5-2B | 2.3B | 85.1 | HuggingFace |
| Qwen/Qwen3.5-2B-Base | 2.3B | 85.1 | HuggingFace |
| google/gemma-2b | 2.5B | 77.2 | HuggingFace |
| google/gemma-1.1-2b-it | 2.5B | 77.2 | HuggingFace |
| google/gemma-2-2b-it | 2.6B | 74.1 | HuggingFace |
| google/gemma-2-2b-jpn-it | 2.6B | 74.1 | HuggingFace |
| Qwen/Qwen2.5-3B-Instruct | 3.1B | 62.7 | Ollama, HF |
| Qwen/Qwen2.5-3B | 3.1B | 62.7 | HuggingFace |
| meta-llama/Llama-3.2-3B-Instruct | 3.2B | 60.3 | HuggingFace |
| meta-llama/Llama-3.2-3B | 3.2B | 60.3 | HuggingFace |
| Qwen/Qwen3-4B-Instruct-2507 | 4.0B | 57.2 | HuggingFace |
| Qwen/Qwen3-4B-Base | 4.0B | 57.2 | HuggingFace |
| Qwen/Qwen3-4B-AWQ | 4.0B | 72.2 | HuggingFace |
| microsoft/Phi-3-mini-4k-instruct | 3.8B | 60.2 | Ollama, HF |
| microsoft/Phi-3.5-mini-instruct | 3.8B | 60.2 | HuggingFace |
| microsoft/Phi-tiny-MoE-instruct | 3.8B | 362.8 | HuggingFace |
| ibm-granite/granite-4.0-h-micro | 3.2B | 72.0 | HuggingFace |

### MoE Models (High Efficiency)

| Model | Size | TPS | Source |
|-------|------|-----|--------|
| ibm-research/PowerMoE-3b | 3.4B | 283.9 | HuggingFace |
| ibm-research/PowerLM-3b | 3.5B | 65.5 | HuggingFace |

### Ollama Commands:
```bash
ollama pull tinyllama
ollama pull llama3.2:1b
ollama pull qwen2.5:1.5b-instruct
ollama pull qwen2:1.5b-instruct
ollama pull qwen2.5:3b-instruct
ollama pull phi3:mini
```

---

## 🖼️ MULTIMODAL Models (80+ models)

### OCR & Vision-Language (<1B)

| Model | Size | TPS | Source |
|-------|------|-----|--------|
| HuggingFaceTB/SmolVLM-256M-Instruct | 256M | 754.8 | HuggingFace |
| HuggingFaceTB/SmolVLM2-256M-Video-Instruct | 256M | 754.8 | HuggingFace |
| stepfun-ai/GOT-OCR-2.0-hf | 561M | 345.4 | HuggingFace |
| HuggingFaceTB/SmolVLM-500M-Instruct | 507M | 381.5 | HuggingFace |
| h2oai/h2ovl-mississippi-800m | 826M | 234.3 | HuggingFace |

### Vision-Language (1B-2B)

| Model | Size | TPS | Source |
|-------|------|-----|--------|
| OpenGVLab/InternVL2-1B | 938M | 206.4 | HuggingFace |
| OpenGVLab/InternVL2_5-1B | 938M | 206.4 | HuggingFace |
| OpenGVLab/InternVL3-1B-hf | 938M | 206.4 | HuggingFace |
| OpenGVLab/InternVL3_5-1B-Instruct | 1.1B | 182.5 | HuggingFace |
| moondream/moondream-2b-2025-04-14-4bit | 1.3B | 147.5 | HuggingFace |
| vikhyatk/moondream2 | 1.9B | 100.5 | HuggingFace |
| Qwen/Qwen3-VL-2B-Instruct | 2.1B | 91.0 | HuggingFace |
| Qwen/Qwen3-VL-2B-Thinking | 2.1B | 91.0 | HuggingFace |

### Vision-Language (2B-4B)

| Model | Size | TPS | Source |
|-------|------|-----|--------|
| Qwen/Qwen2-VL-2B-Instruct-AWQ | 2.4B | 118.9 | Ollama, HF |
| Qwen/Qwen2-VL-2B-Instruct-GPTQ-Int4 | 2.2B | 131.5 | Ollama, HF |
| prithivMLmods/Qwen2-VL-OCR2-2B-Instruct | 2.2B | 87.6 | HuggingFace |
| OpenGVLab/InternVL2-2B | 2.2B | 87.8 | HuggingFace |
| OpenGVLab/InternVL2_5-2B | 2.2B | 87.8 | HuggingFace |
| typhoon-ai/typhoon-ocr1.5-2b | 2.1B | 91.0 | HuggingFace |
| deepseek-ai/deepseek-vl-1.3b-chat | 2.0B | 98.0 | HuggingFace |
| deepseek-ai/DeepSeek-OCR | 3.3B | 68.9 | HuggingFace |
| Isotr0py/deepseek-vl2-tiny | 3.4B | 68.2 | Ollama, HF |
| HuggingFaceTB/SmolVLM-Instruct | 2.2B | 86.2 | Ollama, HF |
| Qwen/Qwen2.5-VL-3B-Instruct | 3.8B | 61.2 | HuggingFace |
| Qwen/Qwen2.5-VL-3B-Instruct-AWQ | 3.8B | 77.3 | HuggingFace |
| OpenGVLab/InternVL2_5-4B | 3.7B | 61.9 | HuggingFace |
| google/paligemma2-3b-mix-224 | 3.0B | 63.8 | HuggingFace |
| LiquidAI/LFM2-VL-3B | 3.0B | 64.6 | HuggingFace |

### MoE Multimodal (High Efficiency)

| Model | Size | TPS | Source |
|-------|------|-----|--------|
| cyankiwi/Qwen3-VL-8B-Instruct-AWQ-4bit | 2.9B | 99.9 | HuggingFace |
| cyankiwi/Qwen3-VL-4B-Instruct-AWQ-4bit | 1.8B | 164.9 | HuggingFace |

### Ollama Commands:
```bash
ollama pull qwen2-vl:2b
huggingface-cli download HuggingFaceTB/SmolVLM-Instruct --local-dir SmolVLM
huggingface-cli download Isotr0py/deepseek-vl2-tiny --local-dir DeepSeek-VL2
```

---

## 🧠 REASONING Models (10+ models)

| Model | Size | TPS | Source |
|-------|------|-----|--------|
| LiquidAI/LFM2.5-1.2B-Thinking | 1.2B | 165.4 | HuggingFace |
| Qwen/Qwen2.5-Math-1.5B-Instruct | 1.5B | 125.4 | HuggingFace |
| Qwen/Qwen2.5-Math-1.5B | 1.5B | 125.4 | HuggingFace |
| KiteFishAI/Minnow-Math-1.5B | 1.6B | 118.5 | HuggingFace |
| Vikhrmodels/QVikhr-3-1.7B-Instruction-noreasoning | 1.7B | 112.5 | HuggingFace |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B | 1.8B | 108.9 | Ollama, HF |
| embedl/Cosmos-Reason2-2B-W4A16-Edge2 | 2.1B | 90.5 | HuggingFace |
| nvidia/NV-Reason-CXR-3B | 3.8B | 61.2 | HuggingFace |
| microsoft/Phi-4-mini-reasoning | 3.8B | 60.5 | Ollama, HF |
| Qwen/Qwen3-4B-Thinking-2507 | 4.0B | 57.2 | HuggingFace |

### Ollama Commands:
```bash
ollama pull deepseek-r1:1.5b
ollama pull phi4-mini-reasoning
```

---

## 🔧 GOOD Fit Models (MoE - High Efficiency)

These models use Mixture of Experts (MoE) architecture, making them efficient despite their name:

| Model | Active Params | TPS | Fit Level | Source |
|-------|---------------|-----|-----------|--------|
| stelterlab/Qwen3-30B-A3B-Instruct-2507-AWQ | 4.6B | 576.5 | Good | HuggingFace |
| cyankiwi/Qwen3-30B-A3B-Instruct-2507-AWQ-4bit | 5.3B | 500.3 | Good | HuggingFace |
| cyankiwi/Qwen3-VL-30B-A3B-Instruct-AWQ-4bit | 5.8B | 623.5 | Good | HuggingFace |
| cyankiwi/Qwen3-Coder-30B-A3B-Instruct-AWQ-4bit | 5.3B | 500.3 | Good | HuggingFace |
| ISTA-DASLab/Mistral-Small-3.1-24B-Instruct-2503-GPTQ-4b-128g | 4.7B | 61.3 | Good | HuggingFace |

---

## 📋 Testing Priority

### High Priority (Fastest TPS)
1. Qwen/Qwen2.5-Coder-0.5B (391.9 TPS)
2. Qwen/Qwen2.5-Coder-0.5B-Instruct (391.9 TPS)
3. Qwen/Qwen2.5-0.5B-Instruct (391.9 TPS)

### Medium Priority (Best Quality/Size Ratio)
1. Qwen/Qwen2.5-1.5B-Instruct (125.4 TPS)
2. meta-llama/Llama-3.2-1B-Instruct (156.7 TPS)
3. microsoft/Phi-3-mini-4k-instruct (60.2 TPS)

### Low Priority (Marginal Fit - may need CPU offloading)
1. microsoft/Orca-2-7b (46.6 TPS) - Q2_K quantization
2. Qwen/Qwen2.5-7B-Instruct (42.9 TPS) - Q2_K quantization

---

## ⚠️ Models That WILL NOT FIT

These models require more than 4GB VRAM:

| Model | Params | Min VRAM | Fit Level |
|-------|--------|----------|-----------|
| qwen3:30b | 30B | 19GB+ | Too Large |
| qwen3-vl:30b | 30B | 20GB+ | Too Large |
| qwen3-coder:30b | 30B | 19GB+ | Too Large |
| orca2:7b | 7B | 4.5GB+ | Marginal (Q2_K) |
| Qwen/Qwen2.5-7B-Instruct | 7.6B | 3.8GB+ | Marginal (Q2_K) |

---

## 📝 Notes

1. **TPS (Tokens Per Second)** - Estimated inference speed on RTX 2050
2. **Fit Level** - Perfect = fits comfortably, Good = fits with MoE efficiency, Marginal = tight fit
3. **Source** - Ollama = available via `ollama pull`, HF = HuggingFace download required
4. **Quantization** - Q4_K_M (default), Q8_0 (higher quality), Q2_K (lowest quality)

---

*Generated by llmfit v0.9.2*