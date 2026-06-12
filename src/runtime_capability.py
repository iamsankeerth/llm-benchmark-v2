"""Runtime capability rules for benchmark queue entries.

This module keeps runtime fit, loadability, and benchability decisions behind
one interface so queue construction, lifecycle, and benchmark adapters do not
drift.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.model_entry import as_model_entry


KNOWN_OLLAMA_TAGS = {
    # Coding
    "Qwen2.5-Coder-0.5B": "qwen2.5-coder:0.5b",
    "Qwen2.5-Coder-0.5B-Instruct": "qwen2.5-coder:0.5b-instruct",
    "Qwen2.5-Coder-1.5B-Instruct": "qwen2.5-coder:1.5b-instruct",
    "Qwen2.5-Coder-1.5B-Instruct-AWQ": "qwen2.5-coder:1.5b-instruct",
    "Qwen2.5-Coder-3B": "qwen2.5-coder:3b",
    "Qwen2.5-Coder-3B-Instruct": "qwen2.5-coder:3b-instruct",
    "starcoder2-3b": "starcoder2:3b",
    "granite-3b-code-base-2k": "granite-code:3b",
    # Chat
    "TinyLlama-1.1B-Chat-v1.0": "tinyllama",
    "Llama-3.2-1B-Instruct": "llama3.2:1b",
    "Llama-3.2-3B-Instruct": "llama3.2:3b",
    "Llama-3.2-3B": "llama3.2:3b",
    "Qwen2.5-1.5B-Instruct": "qwen2.5:1.5b-instruct",
    "Qwen2-1.5B-Instruct": "qwen2:1.5b-instruct",
    "Qwen2.5-3B-Instruct": "qwen2.5:3b-instruct",
    "Qwen3-0.6B": "qwen3:0.6b",
    "Qwen3-1.7B": "qwen3:1.7b",
    "Qwen3-1.7B-Base": "qwen3:1.7b",
    "Qwen3-4B-Base": "qwen3:4b",
    "Qwen3-4B-Instruct-2507": "qwen3:4b",
    "Qwen3.5-0.8B": "qwen3.5:0.8b",
    "Qwen3.5-0.8B-Base": "qwen3.5:0.8b",
    "Qwen3.5-2B": "qwen3.5:2b",
    "Qwen3.5-2B-Base": "qwen3.5:2b",
    "gemma-2b": "gemma:2b",
    "gemma-1.1-2b-it": "gemma:2b",
    "gemma-2-2b-it": "gemma2:2b",
    "gemma-2-2b-jpn-it": "gemma2:2b",
    "Phi-3-mini-4k-instruct": "phi3:mini",
    "Phi-3.5-mini-instruct": "phi3.5:mini",
    # Reasoning
    "Phi-4-mini-reasoning": "phi4-mini-reasoning",
    "DeepSeek-R1-Distill-Qwen-1.5B": "deepseek-r1:1.5b",
    "Qwen2.5-Math-1.5B-Instruct": "qwen2.5-math:1.5b",
    "Qwen2.5-Math-1.5B": "qwen2.5-math:1.5b",
    "Qwen3-4B-Thinking-2507": "qwen3:4b",
}

KNOWN_GGUF_REPOS: set[str] = {
    "bigcode/gpt_bigcode-santacoder",
    "ShahriarFerdoush/llama-3.2-1b-code-instruct",
    "stabilityai/stablelm-2-1_6b-chat",
    "ibm-granite/granite-4.0-h-micro",
    "KiteFishAI/Minnow-Math-1.5B",
    "Vikhrmodels/QVikhr-3-1.7B-Instruction-noreasoning",
    "ibm-research/PowerMoE-3b",
    "ibm-research/PowerLM-3b",
}

VISION_KEYWORDS = [
    "VL-",
    "vl-",
    "VL2",
    "VL3",
    "Vision",
    "OCR",
    "ocr",
    "SmolVLM",
    "InternVL",
    "h2ovl",
    "moondream",
    "deepseek-vl",
    "paligemma",
    "Video",
    "GOT-OCR",
    "Typhoon-OCR",
    "DeepSeek-OCR",
]


@dataclass(frozen=True)
class RuntimeCapability:
    source: str
    resolved_runtime: str
    resolved_model_ref: str
    variant_note: str
    status: str
    ollama_tag: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def runtime_ref(self) -> str:
        return self.ollama_tag or self.resolved_model_ref

    @property
    def is_runnable(self) -> bool:
        return self.status == "pending"

    @property
    def is_llama_benchable(self) -> bool:
        return self.is_runnable and self.resolved_runtime in {"ollama", "huggingface_gguf"}

    @property
    def needs_orchestrated_ollama_lifecycle(self) -> bool:
        return (
            self.status in {"pending", "in_progress"}
            and self.source == "ollama"
            and bool(self.ollama_tag)
        )


def is_vision_model(name: str) -> bool:
    return any(keyword.lower() in name.lower() for keyword in VISION_KEYWORDS)


def is_quantized_variant(name: str) -> bool:
    upper = name.upper()
    return "AWQ" in upper or "GPTQ" in upper or "-FP8" in upper


def make_queue_id(category: str, source: str, name: str, ref: str) -> str:
    normalized_ref = ref.replace("\\", "/")
    return f"{category}:{source}:{name}:{normalized_ref}"


def resolve_runtime_capability(model: dict[str, Any]) -> RuntimeCapability:
    name = model["name"]
    hf_repo = model.get("hf", "")

    if is_vision_model(name):
        return RuntimeCapability(
            source="provider_unsupported",
            resolved_runtime="deferred_vision",
            resolved_model_ref=hf_repo or name,
            variant_note="",
            status="deferred_vision",
        )

    if name in KNOWN_OLLAMA_TAGS:
        tag = KNOWN_OLLAMA_TAGS[name]
        variant_note = ""
        if is_quantized_variant(name):
            variant_note = (
                f"Requested AWQ/GPTQ/FP8 HF variant resolved to standard Ollama "
                f"instruct tag {tag}; results reflect the Ollama tag, not the "
                f"quantised variant."
            )
        return RuntimeCapability(
            source="ollama",
            resolved_runtime="ollama",
            resolved_model_ref=tag,
            variant_note=variant_note,
            status="pending",
            ollama_tag=tag,
        )

    if is_quantized_variant(name):
        return RuntimeCapability(
            source="huggingface",
            resolved_runtime="vllm",
            resolved_model_ref=hf_repo,
            variant_note="AWQ/GPTQ/FP8 quantised repo - requires vLLM runtime",
            status="pending",
        )

    if hf_repo in KNOWN_GGUF_REPOS:
        return RuntimeCapability(
            source="huggingface",
            resolved_runtime="huggingface_gguf",
            resolved_model_ref=hf_repo,
            variant_note="",
            status="pending",
        )

    return RuntimeCapability(
        source="huggingface",
        resolved_runtime="hf_transformers",
        resolved_model_ref=hf_repo,
        variant_note=(
            f"HF repo {hf_repo} loaded via HuggingFace Transformers with 4-bit quantization."
        )
        if hf_repo
        else "No loadable artifacts available for this model.",
        status="pending" if hf_repo else "provider_unsupported",
    )


def capability_for_entry(model_entry: dict[str, Any]) -> RuntimeCapability:
    entry = as_model_entry(model_entry)
    return RuntimeCapability(
        source=entry.source,
        resolved_runtime=entry.resolved_runtime,
        resolved_model_ref=entry.resolved_model_ref,
        variant_note=entry.variant_note,
        status=entry.status,
        ollama_tag=entry.ollama_tag,
    )


def is_llama_benchable(model_entry: dict[str, Any]) -> bool:
    return capability_for_entry(model_entry).is_llama_benchable


def needs_orchestrated_ollama_lifecycle(model_entry: dict[str, Any]) -> bool:
    return capability_for_entry(model_entry).needs_orchestrated_ollama_lifecycle
