"""Model queue builder.

The compatible-model catalog remains the source of truth for candidates. Runtime
capability rules live in ``src.runtime_capability`` so queue construction does
not duplicate provider, variant, and benchability decisions.
"""

from __future__ import annotations

from compatible_models import COMPATIBLE_MODELS, GOOD_FIT_MOE
from src.model_entry import ModelEntry
from src.runtime_capability import (
    KNOWN_GGUF_REPOS,
    KNOWN_OLLAMA_TAGS,
    is_quantized_variant,
    is_vision_model,
    make_queue_id,
    resolve_runtime_capability,
)

# Backward-compatible names used by existing validators and scripts.
_KNOWN_GGUF_REPOS = KNOWN_GGUF_REPOS
_KNOWN_OLLAMA_TAGS = KNOWN_OLLAMA_TAGS


def _is_vl(name: str) -> bool:
    return is_vision_model(name)


def _is_awq_or_gptq(name: str) -> bool:
    return is_quantized_variant(name)


def _make_queue_id(category: str, source: str, name: str, ref: str) -> str:
    return make_queue_id(category, source, name, ref)


def _resolve_identity(model: dict) -> dict:
    return resolve_runtime_capability(model).to_dict()


def build_model_queue() -> list[dict]:
    """Build the benchmark model queue with stable identity metadata."""
    queue: list[dict] = []
    seen_ids: set[str] = set()

    def add_model(model: dict, category: str, fit_level: str, is_moe: bool = False):
        capability = resolve_runtime_capability(model)
        name = model["name"]
        hf_repo = model.get("hf", "")
        queue_id = make_queue_id(
            category,
            capability.source,
            name,
            capability.ollama_tag or hf_repo or name,
        )
        if queue_id in seen_ids:
            return
        seen_ids.add(queue_id)

        queue.append(
            ModelEntry(
                queue_id=queue_id,
                requested_name=name,
                category=category,
                source=capability.source,
                resolved_runtime=capability.resolved_runtime,
                resolved_model_ref=capability.resolved_model_ref,
                variant_note=capability.variant_note,
                ollama_tag=capability.ollama_tag,
                hf_repo=hf_repo,
                size=model.get("size", "?"),
                estimated_tps=model.get("tps", 0),
                fit_level=fit_level,
                is_moe=model.get("moe", is_moe),
                status=capability.status,
            ).to_dict()
        )

    for model in COMPATIBLE_MODELS["coding"]["perfect"]:
        add_model(model, "Coding", "perfect")
    for model in COMPATIBLE_MODELS["coding"]["good"]:
        add_model(model, "Coding", "good", is_moe=True)

    for tier in ("small", "medium", "large", "moe"):
        for model in COMPATIBLE_MODELS["chat"].get(tier, []):
            add_model(model, "Chat", tier, is_moe=model.get("moe", tier == "moe"))

    for tier in ("small", "medium", "large", "good"):
        for model in COMPATIBLE_MODELS.get("multimodal", {}).get(tier, []):
            add_model(model, "Vision", tier, is_moe=model.get("moe", False))

    for model in COMPATIBLE_MODELS["reasoning"].get("perfect", []):
        add_model(model, "Reasoning", "perfect")

    for model in GOOD_FIT_MOE:
        capability = resolve_runtime_capability(model)
        if capability.status == "deferred_vision":
            add_model(model, "Vision", "deferred_vision")
            continue

        name = model["name"]
        if "Coder" in name or "code" in name.lower():
            category = "Coding"
        elif "Reason" in name or "Think" in name or "Math" in name:
            category = "Reasoning"
        else:
            category = "Chat"
        add_model(model, category, "good_fit_moe", is_moe=model.get("moe", True))

    return queue


def queue_summary(queue: list[dict]) -> str:
    """Return a human-readable summary of the queue."""
    total = len(queue)
    runnable = sum(1 for model in queue if model["status"] == "pending")
    unsupported = sum(1 for model in queue if model["status"] == "provider_unsupported")
    deferred = sum(1 for model in queue if model["status"] == "deferred_vision")

    by_category: dict[str, int] = {}
    by_runtime: dict[str, int] = {}
    for model in queue:
        category = model["category"]
        runtime = model.get("resolved_runtime", "?")
        by_category[category] = by_category.get(category, 0) + 1
        by_runtime[runtime] = by_runtime.get(runtime, 0) + 1

    lines = [
        "Model Queue Summary",
        "=" * 40,
        f"Total models in queue: {total}",
        f"  Runnable (pending):  {runnable}",
        f"  Provider unsupported: {unsupported}",
        f"  Deferred vision:      {deferred}",
        "-" * 40,
        "By benchmark category:",
    ]
    for category, count in sorted(by_category.items()):
        lines.append(f"  {category}: {count}")
    lines.append("-" * 40)
    lines.append("By resolved runtime:")
    for runtime, count in sorted(by_runtime.items()):
        lines.append(f"  {runtime}: {count}")
    return "\n".join(lines)
