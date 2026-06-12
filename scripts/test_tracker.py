"""Checkpoint/resume tracker for benchmark progress."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.artifact_store import BenchmarkArtifactStore
from src.progress_projection import ProgressProjection


class TestTracker:
    def __init__(self, progress_file: str = None):
        if progress_file is None:
            base_dir = Path(__file__).parent.parent
            self.progress_file = base_dir / "test_progress.json"
        else:
            self.progress_file = Path(progress_file)
        self.store = BenchmarkArtifactStore(self.progress_file.parent)
        self.store.progress_file = self.progress_file
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_progress_file()

    def _ensure_progress_file(self):
        if not self.progress_file.exists():
            self._save({"last_updated": None, "models": {}})

    def _load(self) -> dict:
        data = self.store.load_progress()
        data.setdefault("last_updated", None)
        data.setdefault("models", {})
        return data

    def _save(self, data: dict):
        self.store.save_progress(data)

    def init_model(
        self,
        model_name: str,
        category: str,
        total_prompts: int = 50,
        model_metadata: dict = None,
    ):
        data = self._load()
        if model_name in data["models"]:
            return

        entry = {
            "model_name": model_metadata.get("requested_name", model_name)
            if model_metadata
            else model_name,
            "category": category,
            "prompts_completed": 0,
            "total_prompts": total_prompts,
            "started_at": None,
            "completed_at": None,
            "csv_file": None,
            "error": None,
            "last_checkpoint": None,
            "status": "pending",
        }
        if model_metadata:
            entry.update(
                {
                    "queue_id": model_metadata.get("queue_id", model_name),
                    "requested_name": model_metadata.get("requested_name", ""),
                    "source": model_metadata.get("source", ""),
                    "resolved_runtime": model_metadata.get("resolved_runtime", ""),
                    "resolved_model_ref": model_metadata.get("resolved_model_ref", ""),
                    "ollama_tag": model_metadata.get("ollama_tag", ""),
                    "hf_repo": model_metadata.get("hf_repo", ""),
                    "variant_note": model_metadata.get("variant_note", ""),
                    "fit_level": model_metadata.get("fit_level", ""),
                    "size": model_metadata.get("size", ""),
                    "estimated_tps": model_metadata.get("estimated_tps", 0),
                    "is_moe": model_metadata.get("is_moe", False),
                }
            )
        data["models"][model_name] = entry
        self._save(data)

    def start_model(self, model_name: str):
        data = self._load()
        if model_name in data["models"]:
            data["models"][model_name]["status"] = "in_progress"
            data["models"][model_name]["started_at"] = datetime.now().isoformat()
            self._save(data)

    def update_checkpoint(self, model_name: str, prompts_completed: int, csv_file: str = None):
        data = self._load()
        if model_name in data["models"]:
            data["models"][model_name]["prompts_completed"] = prompts_completed
            data["models"][model_name]["last_checkpoint"] = datetime.now().isoformat()
            if csv_file:
                data["models"][model_name]["csv_file"] = csv_file
            self._save(data)

    def complete_model(self, model_name: str, csv_file: str):
        data = self._load()
        if model_name in data["models"]:
            total = data["models"][model_name].get("total_prompts", 50)
            data["models"][model_name]["status"] = "completed"
            data["models"][model_name]["prompts_completed"] = total
            data["models"][model_name]["completed_at"] = datetime.now().isoformat()
            data["models"][model_name]["csv_file"] = csv_file
            self._save(data)

    def fail_model(self, model_name: str, error: str):
        data = self._load()
        if model_name in data["models"]:
            data["models"][model_name]["status"] = "failed"
            data["models"][model_name]["error"] = error
            data["models"][model_name]["completed_at"] = datetime.now().isoformat()
            self._save(data)

    def skip_model(self, model_name: str, reason: str, skip_status: str = "skipped"):
        data = self._load()
        if model_name in data["models"]:
            data["models"][model_name]["status"] = skip_status
            data["models"][model_name]["error"] = reason
            data["models"][model_name]["completed_at"] = datetime.now().isoformat()
            self._save(data)

    def is_model_complete(self, model_name: str) -> bool:
        return self._load()["models"].get(model_name, {}).get("status") == "completed"

    def is_model_failed(self, model_name: str) -> tuple[bool, Optional[str]]:
        model_data = self._load()["models"].get(model_name, {})
        if model_data.get("status") == "failed":
            return True, model_data.get("error")
        return False, None

    def get_model_progress(self, model_name: str) -> tuple[str, int, int]:
        model_data = self._load()["models"].get(model_name, {})
        return (
            model_data.get("status", "pending"),
            model_data.get("prompts_completed", 0),
            model_data.get("total_prompts", 50),
        )

    def get_pending_models(self) -> list[dict]:
        pending = []
        for model_name, model_data in self._load()["models"].items():
            if model_data.get("status") in ["pending", "in_progress"]:
                pending.append(
                    {
                        "name": model_name,
                        "category": model_data.get("category"),
                        "status": model_data.get("status"),
                        "prompts_completed": model_data.get("prompts_completed", 0),
                        "total_prompts": model_data.get("total_prompts", 50),
                    }
                )
        return pending

    def get_all_progress(self) -> dict:
        return self._load()

    def generate_status_report(self) -> str:
        return ProgressProjection(self.store).markdown_report(self._load())

    def save_status_to_file(self, filepath: str = None):
        filepath = filepath or self.store.status_file
        report = self.generate_status_report()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        return str(filepath)

    def generate_detailed_model_report(self, model_name: str) -> str:
        model_data = self._load().get("models", {}).get(model_name, {})
        if not model_data:
            return f"No data found for model: {model_name}"

        total = model_data.get("total_prompts", 50)
        completed = model_data.get("prompts_completed", 0)
        display_name = model_data.get("requested_name") or model_data.get("model_name", model_name)
        runtime = model_data.get("resolved_runtime") or model_data.get("source", "?")
        model_ref = (
            model_data.get("resolved_model_ref")
            or model_data.get("ollama_tag")
            or model_data.get("hf_repo", "")
        )
        report = f"""# Detailed Model Report: {display_name}

## Basic Information
- **Queue ID**: {model_name}
- **Category**: {model_data.get('category', 'Unknown')}
- **Status**: {model_data.get('status', 'pending').upper()}
- **Runtime**: {runtime}
- **Resolved Model Ref**: {model_ref}
- **Fit Level**: {model_data.get('fit_level', '?')}
- **Size**: {model_data.get('size', '?')}
- **Est. TPS**: {model_data.get('estimated_tps', 0)}
- **MoE**: {model_data.get('is_moe', False)}

## Progress
- **Prompts Completed**: {completed} / {total}
- **Completion**: {completed / max(total, 1) * 100:.1f}%

## Timing
- **Started At**: {model_data.get('started_at', 'Not started')}
- **Last Checkpoint**: {model_data.get('last_checkpoint', '-')}
- **Completed At**: {model_data.get('completed_at', 'Not completed')}

## Results
- **CSV File**: {model_data.get('csv_file', 'Not generated')}

"""
        variant = model_data.get("variant_note", "")
        if variant:
            report += f"## Variant Note\n- {variant}\n\n"
        if model_data.get("status") == "failed":
            report += f"## Error Information\n- **Error**: {model_data.get('error', 'Unknown error')}\n\n"
        return report


def main():
    tracker = TestTracker()
    parser = argparse.ArgumentParser(description="Test Progress Tracker")
    parser.add_argument("--status", action="store_true", help="Show status report")
    parser.add_argument("--pending", action="store_true", help="List pending models")
    parser.add_argument("--init", metavar="MODEL", help="Initialize a model")
    parser.add_argument("--complete", metavar="MODEL", help="Mark model as complete")
    parser.add_argument("--fail", metavar="MODEL", help="Mark model as failed")
    parser.add_argument("--checkpoint", nargs=2, metavar=("MODEL", "COUNT"), help="Update checkpoint")
    args = parser.parse_args()

    if args.status:
        print(tracker.generate_status_report())
    elif args.pending:
        for model in tracker.get_pending_models():
            print(
                f"{model['name']} ({model['category']}) - "
                f"{model['prompts_completed']}/{model.get('total_prompts', 50)} - "
                f"{model['status']}"
            )
    elif args.init:
        tracker.init_model(args.init, "Unknown")
        print(f"Initialized: {args.init}")


if __name__ == "__main__":
    main()
