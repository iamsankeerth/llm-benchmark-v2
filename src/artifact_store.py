"""Read and write benchmark artifacts through one interface."""

from __future__ import annotations

import json
import os
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.model_entry import as_model_entry, safe_name
from src.result_projection import (
    BenchmarkResultProjection,
    safe_bool as _safe_bool,
    safe_float as _safe_float,
    truthy_success,
)


class BenchmarkArtifactStore:
    """Own artifact paths and raw file reads/writes."""

    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.results_dir = self.base_dir / "results"
        self.phase1_dir = self.results_dir / "phase1"
        self.perf_dir = self.results_dir / "perf"
        self.quality_dir = self.results_dir / "quality"
        self.reports_dir = self.base_dir / "reports"
        self.progress_file = self.base_dir / "test_progress.json"
        self.status_file = self.base_dir / "TEST_STATUS.md"
        self.log_file = self.base_dir / "logs" / "benchmarks.log"
        self.pid_file = self.base_dir / "logs" / "benchmark.pid"

    def projection(self) -> BenchmarkResultProjection:
        return BenchmarkResultProjection(self)

    def load_progress(self) -> dict[str, Any]:
        if not self.progress_file.exists():
            return {"models": {}}
        try:
            with open(self.progress_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {"models": {}}

    def save_progress(self, data: dict[str, Any]) -> None:
        data["last_updated"] = datetime.now().isoformat()
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def read_log_tail(self, n: int = 30) -> list[str]:
        if not self.log_file.exists():
            return []
        try:
            with open(self.log_file, "r", encoding="utf-8", errors="replace") as f:
                return list(deque(f, n))
        except OSError:
            return []

    def find_csv_for_model(self, queue_id: str) -> str | None:
        if not self.phase1_dir.exists():
            return None
        safe = safe_name(queue_id)
        patterns = [f"{safe}_MegaBench_*.csv", f"{safe}_checkpoint.csv"]
        for pattern in patterns:
            matches = sorted(
                self.phase1_dir.glob(pattern),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )
            if matches:
                return str(matches[0])
        return None

    def save_unified_result(self, results_list: list[dict[str, Any]], model: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.phase1_dir.mkdir(parents=True, exist_ok=True)
        csv_path = self.phase1_dir / f"{safe_name(model)}_MegaBench_{timestamp}.csv"
        pd.DataFrame(results_list).to_csv(csv_path, index=False)
        return str(csv_path)

    def save_checkpoint_csv(self, results_list: list[dict[str, Any]], queue_id: str) -> str:
        self.phase1_dir.mkdir(parents=True, exist_ok=True)
        csv_path = self.phase1_dir / f"{safe_name(queue_id)}_checkpoint.csv"
        pd.DataFrame(results_list).to_csv(csv_path, index=False)
        return str(csv_path)

    def phase1_done(self, model_entry: dict[str, Any]) -> bool:
        entry = as_model_entry(model_entry)
        if not self.phase1_dir.exists():
            return False
        safe_id = entry.safe_queue_id
        for path in self.phase1_dir.iterdir():
            if path.name.startswith(safe_id) and (
                path.name.endswith("_checkpoint.csv") or "MegaBench" in path.name
            ):
                return True
        return False

    def llama_bench_result_path(self, queue_id: str) -> Path:
        return self.perf_dir / f"{safe_name(queue_id)}_llama_bench.json"

    def save_llama_bench_result(self, queue_id: str, result: dict[str, Any]) -> Path:
        self.perf_dir.mkdir(parents=True, exist_ok=True)
        result_path = self.llama_bench_result_path(queue_id)
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result_path

    def save_llama_bench_summary(
        self,
        settings: dict[str, Any],
        results: dict[str, Any],
    ) -> Path:
        self.perf_dir.mkdir(parents=True, exist_ok=True)
        summary_path = self.perf_dir / "llama_bench_summary.json"
        summary_path.write_text(
            json.dumps(
                {
                    "timestamp": datetime.now().isoformat(),
                    "settings": settings,
                    "total_models": len(results),
                    "results": results,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return summary_path

    def load_llama_bench_result(self, queue_id: str) -> dict[str, Any] | None:
        result_path = self.llama_bench_result_path(queue_id)
        if not result_path.is_file():
            return None
        try:
            return json.loads(result_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def perf_done(self, model_entry: dict[str, Any]) -> bool:
        entry = as_model_entry(model_entry)
        return self.llama_bench_result_path(entry.queue_id).is_file()

    def quality_result_path(self, model_ref: str) -> Path:
        return self.quality_dir / f"{safe_name(model_ref)}_promptfoo.json"

    def quality_raw_result_path(self, model_ref: str) -> Path:
        return self.quality_dir / f"{safe_name(model_ref)}_promptfoo_raw.json"

    def quality_done(self, model_entry: dict[str, Any]) -> bool:
        entry = as_model_entry(model_entry)
        model_ref = entry.ollama_tag or entry.resolved_model_ref
        return bool(model_ref) and self.quality_result_path(model_ref).is_file()

    def all_phases_done(self, model_entry: dict[str, Any]) -> bool:
        return (
            self.phase1_done(model_entry)
            and self.perf_done(model_entry)
            and self.quality_done(model_entry)
        )

    @staticmethod
    def load_existing_results(csv_path: str) -> list[dict[str, Any]] | None:
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path).to_dict("records")
        return None

    @staticmethod
    def _truthy_success(value: Any) -> bool:
        return truthy_success(value)

    def compute_csv_metrics(self, csv_path: str) -> dict[str, Any]:
        return self.projection().compute_csv_metrics(csv_path)

    def compute_quality_metrics(self, model_name: str) -> dict[str, Any]:
        return self.projection().compute_quality_metrics(model_name)

    def model_prompts(self, queue_id: str) -> dict[str, Any] | None:
        return self.projection().model_prompts(queue_id)

    def compute_difficulty_stats(
        self, csv_path: str, total_per_diff: int = 10
    ) -> dict[str, Any]:
        return self.projection().compute_difficulty_stats(csv_path, total_per_diff)

    def load_llama_bench(self) -> dict[str, Any]:
        return self.projection().load_llama_bench()

    def load_promptfoo(self) -> dict[str, Any]:
        return self.projection().load_promptfoo()
