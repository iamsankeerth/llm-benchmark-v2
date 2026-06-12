"""Benchmark result projections built from stored artifacts."""

from __future__ import annotations

import csv
import json
import os
from typing import Any

from src.model_entry import safe_name


class BenchmarkResultProjection:
    """Turn artifact files into metric and prompt payloads."""

    def __init__(self, store: Any):
        self.store = store

    def compute_csv_metrics(self, csv_path: str) -> dict[str, Any]:
        if not csv_path or not os.path.isfile(csv_path):
            return {}
        try:
            rows: list[dict[str, str]] = []
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows.extend(reader)
            if not rows:
                return {}

            tps_vals = [
                float(r["tps"])
                for r in rows
                if r.get("tps") and float(r.get("tps", 0) or 0) > 0
            ]
            lat_vals = [
                float(r["latency"])
                for r in rows
                if r.get("latency") and float(r.get("latency", 0) or 0) > 0
            ]
            vram_vals = [
                float(r["peak_vram_mb"])
                for r in rows
                if r.get("peak_vram_mb") and float(r.get("peak_vram_mb", 0) or 0) > 0
            ]
            t0_vals = [r.get("temp_0.0_success", "") for r in rows]
            t0_ok = sum(1 for value in t0_vals if truthy_success(value))

            return {
                "tps_avg": round(sum(tps_vals) / len(tps_vals), 1) if tps_vals else 0,
                "latency_avg": round(sum(lat_vals) / len(lat_vals), 2) if lat_vals else 0,
                "vram_peak": round(max(vram_vals), 0) if vram_vals else 0,
                "json_success_rate": round(t0_ok / len(rows) * 100, 1) if rows else 0,
            }
        except Exception:
            return {}

    def compute_quality_metrics(self, model_name: str) -> dict[str, Any]:
        if not self.store.quality_dir.exists():
            return {}
        try:
            safe_candidates = [safe_name(model_name), safe_name(model_name).replace(".", "_")]
            raw_file = self.store.quality_dir / f"{safe_candidates[0]}_promptfoo_raw.json"
            if not raw_file.exists():
                for candidate in self.store.quality_dir.glob("*_promptfoo_raw.json"):
                    folded_name = candidate.name.replace("_", "").replace(".", "")
                    if any(
                        safe.replace("_", "").replace(".", "") in folded_name
                        for safe in safe_candidates
                    ):
                        raw_file = candidate
                        break
            if not raw_file.exists():
                return {}

            with open(raw_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            results = data.get("results", {}).get("results", [])
            if not results:
                return {}

            passed = sum(1 for result in results if result.get("success"))
            total = len(results)
            categories: dict[str, dict[str, int]] = {}
            for result in results:
                desc = result.get("testCase", {}).get("description", "")
                category = desc.split(":")[0].strip() if ":" in desc else "Other"
                categories.setdefault(category, {"passed": 0, "total": 0})
                categories[category]["total"] += 1
                if result.get("success"):
                    categories[category]["passed"] += 1

            def category_rate(name: str) -> float:
                stats = categories.get(name, {"passed": 0, "total": 0})
                return round(stats["passed"] / stats["total"] * 100, 1) if stats["total"] else 0

            return {
                "pass_rate": round(passed / total * 100, 1) if total else 0,
                "coding_pass_rate": category_rate("Coding"),
                "chat_pass_rate": category_rate("Chat"),
                "reasoning_pass_rate": category_rate("Reasoning"),
                "structured_pass_rate": category_rate("Structured"),
                "total_tests": total,
                "passed": passed,
            }
        except Exception:
            return {}

    def model_prompts(self, queue_id: str) -> dict[str, Any] | None:
        tracked = self.store.load_progress().get("models", {}).get(queue_id, {})
        csv_path = tracked.get("csv_file", "")
        if not csv_path or not os.path.isfile(csv_path):
            csv_path = self.store.find_csv_for_model(queue_id)
        if not csv_path or not os.path.isfile(csv_path):
            return None

        prompts = []
        with open(csv_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                prompts.append(
                    {
                        "prompt_id": safe_float(row.get("prompt_id")),
                        "difficulty": row.get("difficulty", ""),
                        "tps": safe_float(row.get("tps")),
                        "ttft": safe_float(row.get("ttft")),
                        "latency": safe_float(row.get("latency")),
                        "vram_mb": safe_float(row.get("peak_vram_mb")),
                        "temp_0.0_success": safe_bool(row.get("temp_0.0_success")),
                        "temp_0.7_success": safe_bool(row.get("temp_0.7_success")),
                        "temp_1.0_success": safe_bool(row.get("temp_1.0_success")),
                        "error": (row.get("error") or "").strip()[:100] or None,
                    }
                )
        return {
            "queue_id": queue_id,
            "model": tracked.get("model_name", queue_id),
            "csv_file": csv_path,
            "prompts": prompts,
        }

    def compute_difficulty_stats(
        self, csv_path: str, total_per_diff: int = 10
    ) -> dict[str, Any]:
        stats = {
            diff: {"count": total_per_diff, "avg_latency": 0, "completed": 0}
            for diff in ["easy", "medium", "hard", "adversarial", "long_context"]
        }
        if not csv_path or not os.path.isfile(csv_path):
            return stats
        try:
            by_diff: dict[str, list[float]] = {}
            with open(csv_path, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    diff = row.get("difficulty", "")
                    latency = float(row.get("latency", 0) or 0)
                    by_diff.setdefault(diff, [])
                    if latency > 0:
                        by_diff[diff].append(latency)
            for diff, values in by_diff.items():
                if diff in stats:
                    stats[diff]["avg_latency"] = (
                        round(sum(values) / len(values), 2) if values else 0
                    )
                    stats[diff]["completed"] = len(values)
        except Exception:
            pass
        return stats

    def load_llama_bench(self) -> dict[str, Any]:
        perf_data: dict[str, Any] = {}
        summary_file = self.store.perf_dir / "llama_bench_summary.json"
        if summary_file.is_file():
            try:
                with open(summary_file, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                for qid, result in raw.get("results", {}).items():
                    key = result.get("model_name", qid)
                    perf_data[key] = {
                        "tg_tps": result.get("tg_tps", 0),
                        "pp_tps": result.get("pp_tps", 0),
                        "tg_stddev": result.get("tg_stddev", 0),
                        "pp_stddev": result.get("pp_stddev", 0),
                    }
                return perf_data
            except Exception:
                pass

        for path in self.store.perf_dir.glob("*_llama_bench.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    result = json.load(f)
                key = result.get("model_name", path.name)
                perf_data[key] = {
                    "tg_tps": result.get("tg_tps", 0),
                    "pp_tps": result.get("pp_tps", 0),
                    "tg_stddev": result.get("tg_stddev", 0),
                    "pp_stddev": result.get("pp_stddev", 0),
                }
            except Exception:
                pass
        return perf_data

    def load_promptfoo(self) -> dict[str, Any]:
        quality_data: dict[str, Any] = {}
        summary_file = self.store.quality_dir / "promptfoo_summary.json"
        if summary_file.is_file():
            try:
                with open(summary_file, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                for tag, result in raw.get("results", {}).items():
                    quality_data[tag] = {
                        "pass_rate": result.get("pass_rate", 0),
                        "passed": result.get("passed", 0),
                        "total_tests": result.get("total_tests", 0),
                    }
                return quality_data
            except Exception:
                pass

        for path in self.store.quality_dir.glob("*_promptfoo.json"):
            if path.name.endswith("_promptfoo_raw.json"):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    result = json.load(f)
                tag = result.get("model", path.name)
                quality_data[tag] = {
                    "pass_rate": result.get("pass_rate", 0),
                    "passed": result.get("passed", 0),
                    "total_tests": result.get("total_tests", 0),
                }
            except Exception:
                pass
        return quality_data


def truthy_success(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def safe_float(value: Any) -> float | None:
    try:
        return round(float(value), 2) if value and str(value).strip() else None
    except (TypeError, ValueError):
        return None


def safe_bool(value: Any) -> bool | None:
    return truthy_success(value) if value and str(value).strip() else None
