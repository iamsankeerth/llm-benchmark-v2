# AI Model Download Commands (Ollama + Hugging Face)

## Hugging Face Commands

``` bash
huggingface-cli download cyankiwi/Qwen3-VL-30B-A3B-Instruct-AWQ-4bit --local-dir Qwen3-VL-30B-A3B
huggingface-cli download cyankiwi/Qwen3-30B-A3B-Instruct-2507-AWQ-4bit --local-dir Qwen3-30B-A3B
huggingface-cli download cyankiwi/Qwen3-Coder-30B-A3B-Instruct-AWQ-4bit --local-dir Qwen3-Coder-30B-A3B
huggingface-cli download stelterlab/Qwen3-30B-A3B-Instruct-2507-AWQ --local-dir Qwen3-30B-A3B-Instruct-2507-AWQ
huggingface-cli download Vikhrmodels/QVikhr-3-1.7B-Instruction-noreasoning --local-dir QVikhr-3-1.7B
huggingface-cli download Qwen/Qwen2.5-3B-Instruct-AWQ --local-dir Qwen2.5-3B
huggingface-cli download Qwen/Qwen2.5-Coder-1.5B-Instruct-AWQ --local-dir Qwen2.5-Coder-1.5B
huggingface-cli download Qwen/Qwen2.5-Coder-3B-Instruct --local-dir Qwen2.5-Coder-3B
huggingface-cli download Qwen/Qwen2.5-Coder-3B --local-dir Qwen2.5-Coder-3B-base
huggingface-cli download Qwen/Qwen2.5-Coder-0.5B-Instruct --local-dir Qwen2.5-Coder-0.5B
huggingface-cli download Qwen/Qwen2.5-Coder-0.5B --local-dir Qwen2.5-Coder-0.5B-base
huggingface-cli download Qwen/Qwen2.5-1.5B-Instruct --local-dir Qwen2.5-1.5B
huggingface-cli download Qwen/Qwen2-1.5B-Instruct --local-dir Qwen2-1.5B
huggingface-cli download meta-llama/Llama-3.2-1B-Instruct --local-dir Llama-3.2-1B
huggingface-cli download ShahriarFerdoush/llama-3.2-1b-code-instruct --local-dir llama-3.2-1b-code-instruct
huggingface-cli download microsoft/Phi-4-mini-reasoning --local-dir Phi-4-mini
huggingface-cli download microsoft/Orca-2-7b --local-dir Orca-2-7b
huggingface-cli download microsoft/Phi-tiny-MoE-instruct --local-dir Phi-tiny-MoE
huggingface-cli download nvidia/NV-Reason-CXR-3B --local-dir NV-Reason
huggingface-cli download deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --local-dir DeepSeek-R1
huggingface-cli download typhoon-ai/typhoon-ocr1.5-2b --local-dir Typhoon-OCR
huggingface-cli download bigcode/starcoder2-3b --local-dir Starcoder2
huggingface-cli download ibm-granite/granite-3b-code-base-2k --local-dir Granite
huggingface-cli download deepseek-ai/deepseek-vl-1.3b-chat --local-dir DeepSeek-VL
huggingface-cli download Isotr0py/deepseek-vl2-tiny --local-dir DeepSeek-VL2
huggingface-cli download HuggingFaceTB/SmolVLM-Instruct --local-dir SmolVLM
huggingface-cli download Qwen/Qwen2-VL-2B-Instruct-GPTQ-Int4 --local-dir Qwen2-VL
huggingface-cli download Qwen/Qwen2-VL-2B-Instruct-AWQ --local-dir Qwen2-VL-AWQ
```

## Ollama Commands

``` bash
ollama pull qwen3-vl:30b
ollama pull qwen3:30b
ollama pull qwen3-coder:30b
ollama pull qwen2.5:3b-instruct
ollama pull qwen2.5:1.5b-instruct
ollama pull qwen2:1.5b-instruct
ollama pull qwen2.5-coder:1.5b-instruct
ollama pull qwen2.5-coder:3b-instruct
ollama pull qwen2.5-coder:3b
ollama pull qwen2.5-coder:0.5b-instruct
ollama pull qwen2.5-coder:0.5b
ollama pull llama3.2:1b
ollama pull phi4-mini-reasoning
ollama pull orca2:7b
ollama pull deepseek-r1:1.5b
ollama pull phi3:mini
ollama pull granite-code:3b
```
