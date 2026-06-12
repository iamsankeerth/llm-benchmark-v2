"""Progress projections for Markdown status and live dashboard payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from src.artifact_store import BenchmarkArtifactStore
from src.result_projection import BenchmarkResultProjection


STATUS_ICONS = {
    "completed": "[done]",
    "in_progress": "[run]",
    "failed": "[fail]",
    "pending": "[wait]",
    "skipped": "[skip]",
    "provider_unsupported": "[unsupported]",
    "deferred_vision": "[vision]",
}


class ProgressProjection:
    """Project benchmark progress through one status interface."""

    def __init__(
        self,
        store: BenchmarkArtifactStore | None = None,
        queue_loader: Callable[[], list[dict[str, Any]]] | None = None,
        result_projection: BenchmarkResultProjection | None = None,
    ):
        self.store = store or BenchmarkArtifactStore()
        self.queue_loader = queue_loader or self._load_model_queue
        self.results = result_projection or BenchmarkResultProjection(self.store)

    @staticmethod
    def _load_model_queue() -> list[dict[str, Any]]:
        try:
            from src.model_queue import build_model_queue

            return build_model_queue()
        except Exception:
            return []

    def markdown_report(self, progress: dict[str, Any] | None = None) -> str:
        progress = progress or self.store.load_progress()
        models = progress.get("models", {})
        counts = self.counts(models)
        global_eta = self.global_eta(models)

        report = f"""# Test Progress Dashboard
**Last Updated**: {progress.get('last_updated', 'Never')}

## Summary
- **Total Pipeline ETA**: {global_eta} ({counts['pending'] + counts['in_progress']} models remaining)
- **Total Models**: {counts['total']}
- **Completed**: {counts['completed']}
- **In Progress**: {counts['in_progress']}
- **Failed**: {counts['failed']}
- **Skipped**: {counts['skipped']}
- **Pending**: {counts['pending']}

## Model Status by Category

"""
        categories: dict[str, list[tuple[str, dict[str, Any]]]] = {}
        for model_name, model_data in models.items():
            category = model_data.get("category", "Unknown")
            categories.setdefault(category, []).append((model_name, model_data))

        for category, model_list in sorted(categories.items()):
            report += f"### {category} ({len(model_list)} models)\n\n"
            report += "| Model | Source/Runtime | Status | Progress | Time Spent | ETA | Error |\n"
            report += "|-------|---------------|--------|----------|------------|-----|-------|\n"
            for key, model_data in model_list:
                report += self.markdown_model_row(key, model_data)
            report += "\n"
        return report

    def markdown_model_row(self, key: str, model_data: dict[str, Any]) -> str:
        status = model_data.get("status", "pending")
        icon = STATUS_ICONS.get(status, "[?]")
        display_name = model_data.get("requested_name") or model_data.get("model_name", key)
        runtime = model_data.get("resolved_runtime") or model_data.get("source", "?")
        completed = model_data.get("prompts_completed", 0)
        total = model_data.get("total_prompts", 50)
        time_spent = "-"
        eta = "-"

        if model_data.get("started_at"):
            start = datetime.fromisoformat(model_data["started_at"])
            if status == "completed" and model_data.get("completed_at"):
                end = datetime.fromisoformat(model_data["completed_at"])
                time_spent = f"{(end - start).total_seconds() / 60:.1f}m"
            elif status in ["in_progress", "failed"]:
                now = datetime.fromisoformat(model_data.get("last_checkpoint", datetime.now().isoformat()))
                elapsed = (now - start).total_seconds()
                time_spent = f"{elapsed / 60:.1f}m"
                if status == "in_progress" and completed > 0:
                    remaining = total - completed
                    eta_mins = (elapsed / completed * remaining) / 60
                    eta = f"~{eta_mins:.1f}m" if remaining > 0 else "Finishing..."

        if status in ("failed", "skipped", "provider_unsupported", "deferred_vision"):
            error = (model_data.get("error") or "Unknown").replace("\n", " ")[:40]
            return (
                f"| {display_name} | {runtime} | {icon} {status} | {completed}/{total} "
                f"| {time_spent} | - | {error}... |\n"
            )
        return (
            f"| {display_name} | {runtime} | {icon} {status.title()} | {completed}/{total} "
            f"| {time_spent} | {eta} | - |\n"
        )

    def live_payload(
        self,
        process_alive: bool,
        process_pid: int | None,
        gpu: dict[str, str],
        log_tail: list[str],
        progress: dict[str, Any] | None = None,
        queue: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        progress = progress or self.store.load_progress()
        tracked_models = progress.get("models", {})
        queue = queue if queue is not None else self.queue_loader()

        current = self.current_model_state(tracked_models)
        status = current["status"]
        if process_alive and status == "idle":
            status = "running"
        if not process_alive and status == "in_progress":
            status = "stopped"

        all_models = self.all_models(queue, tracked_models)
        pending_count = sum(1 for model in all_models if model["status"] == "pending")
        completed_models, failed_models = self.completed_and_failed(tracked_models)
        current_phase, current_phase_label = detect_phase(log_tail)
        if current_phase == "idle" and status == "in_progress":
            current_phase = "test_a"
            current_phase_label = "Test A: Phase 1 (CSV Data)"

        difficulty_stats = {}
        if status == "in_progress":
            for key, data in tracked_models.items():
                if data.get("status") == "in_progress":
                    csv_path = data.get("csv_file", "") or self.store.find_csv_for_model(key)
                    difficulty_stats = self.results.compute_difficulty_stats(csv_path)
                    break

        current_index = current["current_model_index"]
        if current_index == 0:
            current_index = len(completed_models) + (1 if status == "in_progress" else 0)

        return {
            "process_alive": process_alive,
            "process_pid": process_pid,
            "gpu": gpu,
            "current_model": current["current_model"],
            "current_model_index": current_index,
            "total_models": len(all_models),
            "prompts_completed": current["prompts_completed"],
            "total_prompts": current["total_prompts"],
            "status": status,
            "elapsed_time": current["elapsed_time"],
            "eta": current["eta"],
            "current_phase": current_phase,
            "current_phase_label": current_phase_label,
            "per_prompt_eta": calc_per_prompt_eta(
                current["elapsed_sec"], current["prompts_completed"]
            )
            if status == "in_progress"
            else "-",
            "total_model_eta": calc_total_model_eta(
                current_phase,
                current["prompts_completed"],
                current["total_prompts"],
                current["elapsed_sec"],
            )
            if status == "in_progress"
            else "-",
            "phase_eta": current["eta"],
            "difficulty_stats": difficulty_stats,
            "last_updated": current["last_updated"] or progress.get("last_updated", ""),
            "completed_models": completed_models,
            "failed_models": failed_models,
            "pending_count": pending_count,
            "all_models": all_models,
            "log_tail": [line.rstrip() for line in log_tail],
        }

    def current_model_state(self, tracked_models: dict[str, dict[str, Any]]) -> dict[str, Any]:
        current_model = None
        current_model_index = 0
        prompts_completed = 0
        total_prompts = 0
        status = "idle"
        elapsed_time = "-"
        eta = "-"
        elapsed_sec = 0.0
        last_updated = ""
        completed_seen = 0

        for key, data in tracked_models.items():
            model_status = data.get("status", "pending")
            model_name = data.get("model_name") or data.get("requested_name", key)
            if model_status == "completed":
                completed_seen += 1
            elif model_status == "in_progress":
                current_model = model_name
                prompts_completed = data.get("prompts_completed", 0)
                total_prompts = data.get("total_prompts", 50)
                status = "in_progress"
                elapsed_time = format_elapsed(data.get("started_at"))
                eta = calc_eta(data.get("started_at"), prompts_completed, total_prompts)
                last_updated = data.get("last_checkpoint", "")
                current_model_index = completed_seen + 1
                if data.get("started_at"):
                    try:
                        start = datetime.fromisoformat(data["started_at"])
                        elapsed_sec = (datetime.now() - start).total_seconds()
                    except Exception:
                        elapsed_sec = 0.0

        return {
            "current_model": current_model,
            "current_model_index": current_model_index,
            "prompts_completed": prompts_completed,
            "total_prompts": total_prompts,
            "status": status,
            "elapsed_time": elapsed_time,
            "eta": eta,
            "elapsed_sec": elapsed_sec,
            "last_updated": last_updated,
        }

    def completed_and_failed(
        self, tracked_models: dict[str, dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        completed_models = []
        failed_models = []
        for key, data in tracked_models.items():
            model_status = data.get("status", "pending")
            model_name = data.get("model_name") or data.get("requested_name", key)
            if model_status == "completed":
                csv_path = data.get("csv_file", "")
                completed_models.append(
                    {
                        "name": model_name,
                        "category": data.get("category", ""),
                        "prompts_completed": data.get("prompts_completed", 0),
                        "csv_file": csv_path,
                        **self.results.compute_csv_metrics(csv_path),
                        **self.results.compute_quality_metrics(model_name),
                    }
                )
            elif model_status == "failed":
                failed_models.append(
                    {
                        "name": model_name,
                        "category": data.get("category", ""),
                        "error": (data.get("error") or "Unknown")[:200],
                    }
                )
        return completed_models, failed_models

    def all_models(
        self, queue: list[dict[str, Any]], tracked_models: dict[str, dict[str, Any]]
    ) -> list[dict[str, Any]]:
        all_models = []
        for model in queue:
            qid = model["queue_id"]
            name = model.get("requested_name", model.get("name", ""))
            tracked = tracked_models.get(qid, {})
            model_status = tracked.get("status", model.get("status", "pending"))
            entry = {
                "queue_id": qid,
                "name": name,
                "category": model.get("category", ""),
                "status": model_status,
                "source": model.get("source", ""),
                "resolved_runtime": model.get("resolved_runtime", ""),
                "size": model.get("size", "?"),
                "prompts_completed": tracked.get("prompts_completed", 0),
                "total_prompts": tracked.get("total_prompts", 50),
                "elapsed": format_elapsed(tracked.get("started_at"))
                if tracked.get("started_at")
                else "-",
                "tps_avg": 0,
                "latency_avg": 0,
                "vram_peak": 0,
                "json_success_rate": 0,
                "pass_rate": 0,
                "coding_pass_rate": 0,
                "chat_pass_rate": 0,
                "reasoning_pass_rate": 0,
                "structured_pass_rate": 0,
                "total_tests": 0,
                "passed": 0,
                "error": "",
            }

            csv_path = tracked.get("csv_file", "")
            if not csv_path and model_status in ("completed", "in_progress"):
                csv_path = self.store.find_csv_for_model(qid)
            if csv_path:
                entry.update(self.results.compute_csv_metrics(csv_path))
            if model_status == "completed":
                entry.update(self.results.compute_quality_metrics(name))
            if model_status == "failed":
                entry["error"] = (tracked.get("error") or "")[:200]
            all_models.append(entry)
        return all_models

    @staticmethod
    def counts(models: dict[str, dict[str, Any]]) -> dict[str, int]:
        return {
            "total": len(models),
            "completed": sum(1 for model in models.values() if model.get("status") == "completed"),
            "in_progress": sum(
                1 for model in models.values() if model.get("status") == "in_progress"
            ),
            "failed": sum(1 for model in models.values() if model.get("status") == "failed"),
            "skipped": sum(
                1
                for model in models.values()
                if model.get("status") in ("skipped", "provider_unsupported", "deferred_vision")
            ),
            "pending": sum(1 for model in models.values() if model.get("status") == "pending"),
        }

    @staticmethod
    def global_eta(models: dict[str, dict[str, Any]]) -> str:
        completed_points = 0
        elapsed_sec = 0.0
        for model_data in models.values():
            status = model_data.get("status")
            if not model_data.get("started_at"):
                continue
            start = datetime.fromisoformat(model_data["started_at"])
            if status == "completed" and model_data.get("completed_at"):
                end = datetime.fromisoformat(model_data["completed_at"])
                elapsed_sec += (end - start).total_seconds()
                completed_points += model_data.get("total_prompts", 50)
            elif status in ["in_progress", "failed"]:
                now = datetime.fromisoformat(
                    model_data.get("last_checkpoint", datetime.now().isoformat())
                )
                elapsed_sec += (now - start).total_seconds()
                completed_points += model_data.get("prompts_completed", 0)

        if completed_points <= 0:
            return "Calculating..."
        avg_sec_per_point = elapsed_sec / completed_points
        total_points = sum(model.get("total_prompts", 50) for model in models.values())
        remaining = total_points - completed_points
        eta_sec = avg_sec_per_point * remaining
        hours = int(eta_sec // 3600)
        minutes = int((eta_sec % 3600) // 60)
        return f"~{hours}h {minutes}m" if eta_sec > 0 else "Finishing..."


def calc_eta(started_at: str, completed: int, total: int) -> str:
    if not started_at or completed <= 0:
        return "Calculating..."
    try:
        start = datetime.fromisoformat(started_at)
        elapsed = (datetime.now() - start).total_seconds()
        if elapsed <= 0:
            return "Calculating..."
        eta_sec = (elapsed / completed) * (total - completed)
        if eta_sec < 60:
            return f"~{int(eta_sec)}s"
        if eta_sec < 3600:
            return f"~{int(eta_sec / 60)}m"
        return f"~{int(eta_sec // 3600)}h {int((eta_sec % 3600) // 60)}m"
    except Exception:
        return "Calculating..."


def format_elapsed(started_at: str) -> str:
    if not started_at:
        return "-"
    try:
        elapsed = (datetime.now() - datetime.fromisoformat(started_at)).total_seconds()
        if elapsed < 60:
            return f"{int(elapsed)}s"
        if elapsed < 3600:
            return f"{int(elapsed / 60)}m"
        return f"{int(elapsed // 3600)}h {int((elapsed % 3600) // 60)}m"
    except Exception:
        return "-"


def detect_phase(log_tail: list[str]) -> tuple[str, str]:
    markers = [
        (">>> Downloading", "download", "Download"),
        ("--- Running Test A", "test_a", "Test A: CSV Data"),
        ("--- Running Test B", "test_b", "Test B: llama-bench"),
        ("--- Running Test C", "test_c", "Test C: promptfoo"),
        (">>> Deleting", "delete", "Delete"),
    ]
    for line in reversed(log_tail):
        stripped = line.strip()
        for marker, phase_id, phase_label in markers:
            if marker in stripped:
                return phase_id, phase_label
    return "idle", "Idle"


def calc_per_prompt_eta(elapsed_sec: float, prompts_completed: int) -> str:
    if prompts_completed <= 0:
        return "Calculating..."
    avg = elapsed_sec / prompts_completed
    return f"~{avg:.0f}s" if avg < 60 else f"~{avg / 60:.1f}m"


def calc_total_model_eta(
    phase: str,
    prompts_completed: int,
    total_prompts: int,
    elapsed_sec: float,
    avg_test_b: float = 120,
    avg_test_c: float = 300,
) -> str:
    if prompts_completed <= 0:
        return "Calculating..."
    avg_per_prompt = elapsed_sec / prompts_completed
    remaining_prompts = total_prompts - prompts_completed
    if phase == "test_a":
        eta = (remaining_prompts * avg_per_prompt) + avg_test_b + avg_test_c
    elif phase == "test_b":
        eta = avg_test_b + avg_test_c
    elif phase == "test_c":
        eta = avg_test_c
    elif phase == "download":
        eta = (total_prompts * avg_per_prompt) + avg_test_b + avg_test_c
    else:
        eta = 0
    if eta < 60:
        return f"~{int(eta)}s"
    if eta < 3600:
        return f"~{int(eta / 60)}m"
    return f"~{int(eta // 3600)}h {int((eta % 3600) // 60)}m"
