"""Phase 1 benchmark pass.

This module owns the full Phase 1 pass: queue filtering, prompt selection,
runtime acquisition, per-prompt execution, structured-output checks, checkpoint
resume, and final progress status.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from config import MAX_NEW_TOKENS
from scripts.test_tracker import TestTracker
from src.artifact_store import BenchmarkArtifactStore
from src.benchmarker import Benchmarker
from src.lifecycle import RuntimeHandle, acquire_runtime, cleanup_runtime
from src.model_comparator import ModelComparator
from src.model_entry import as_model_entry
from src.schemas import get_schema_for_category
from src.structured_output import StructuredOutputTester


LogFn = Callable[..., None]

CATEGORY_PROMPT_MAP = {
    "Coding": "Coding Generation",
    "Reasoning": "Medium Reasoning",
    "Chat": "Chat & Generation",
    "Vision": "Multimodal Vision",
}


@dataclass
class Phase1RunConfig:
    model_queue: list[dict[str, Any]]
    prompts_dir: str | Path
    models_dir: str | Path
    temps_to_test: list[float]
    phase2_prompt_limit: int | None
    smoke_run_prompts: int = 0
    slow_model_threshold_secs: int = 0
    single_model_env: str = "BENCHMARK_SINGLE_MODEL"

    @classmethod
    def from_project_config(cls) -> "Phase1RunConfig":
        from config import (
            MODEL_QUEUE,
            MODELS_DIR,
            PHASE2_PROMPT_LIMIT,
            PROMPTS_DIR,
            TEMPS_TO_TEST,
        )

        try:
            from config import SLOW_MODEL_THRESHOLD_SECS, SMOKE_RUN_PROMPTS
        except ImportError:
            SMOKE_RUN_PROMPTS = 0
            SLOW_MODEL_THRESHOLD_SECS = 0

        return cls(
            model_queue=MODEL_QUEUE,
            prompts_dir=PROMPTS_DIR,
            models_dir=MODELS_DIR,
            temps_to_test=TEMPS_TO_TEST,
            phase2_prompt_limit=PHASE2_PROMPT_LIMIT,
            smoke_run_prompts=SMOKE_RUN_PROMPTS,
            slow_model_threshold_secs=SLOW_MODEL_THRESHOLD_SECS,
        )

    @property
    def phase2_limit(self) -> int:
        if self.phase2_prompt_limit is None:
            return 2**62
        return self.phase2_prompt_limit


class Phase1BenchmarkPass:
    def __init__(
        self,
        config: Phase1RunConfig | None = None,
        tracker: TestTracker | None = None,
        store: BenchmarkArtifactStore | None = None,
        benchmarker: Benchmarker | None = None,
        structured_tester: StructuredOutputTester | None = None,
        acquire_runtime_fn: Callable[[dict[str, Any]], RuntimeHandle | None] | None = None,
        cleanup_runtime_fn: Callable[[RuntimeHandle | None], None] | None = None,
        log: LogFn | None = None,
        env: dict[str, str] | None = None,
    ):
        self.config = config or Phase1RunConfig.from_project_config()
        self.tracker = tracker or TestTracker()
        self.store = store or BenchmarkArtifactStore()
        self.benchmarker = benchmarker or Benchmarker()
        self.structured_tester = structured_tester or StructuredOutputTester()
        self.acquire_runtime_fn = acquire_runtime_fn or (
            lambda model_entry: acquire_runtime(model_entry, log=self.log)
        )
        self.cleanup_runtime_fn = cleanup_runtime_fn or (
            lambda handle: cleanup_runtime(handle, log=self.log)
        )
        self.log = log or print
        self.env = env if env is not None else os.environ

    def run(self) -> None:
        self.log("Starting Unified LLM Mega-Benchmark Pipeline with Checkpoint/Resume")
        self.log("=" * 60)

        Path(self.config.models_dir).mkdir(parents=True, exist_ok=True)
        all_prompts = self.load_prompts()
        if all_prompts is None:
            return

        total_models = len(self.config.model_queue)
        runnable = sum(1 for model in self.config.model_queue if as_model_entry(model).is_runnable)
        self.log(f"Loaded {len(all_prompts)} prompts from dataset")
        self.log(f"Model queue: {total_models} total ({runnable} runnable)")

        for idx, model_entry in enumerate(self.config.model_queue, 1):
            self.run_model(idx, total_models, model_entry, all_prompts)

        self.log("\n" + "=" * 60)
        self.log("ALL MODELS PROCESSED!")
        self.log("=" * 60)
        self.log("\nGenerating Final Report...")
        ModelComparator().run_offline_report()

    def load_prompts(self) -> list[dict[str, Any]] | None:
        prompts_path = Path(self.config.prompts_dir) / "benchmark_prompts.json"
        if not prompts_path.exists():
            self.log("prompts.json not found!")
            return None
        return json.loads(prompts_path.read_text(encoding="utf-8"))

    def run_model(
        self,
        idx: int,
        total_models: int,
        model_entry: dict[str, Any],
        all_prompts: list[dict[str, Any]],
    ) -> None:
        entry = as_model_entry(model_entry)
        queue_id = entry.queue_id

        target_model = self.env.get(self.config.single_model_env)
        if target_model and queue_id != target_model:
            return

        target_category = self.target_category_for(entry.category)
        filtered_prompts = [
            prompt for prompt in all_prompts if prompt["category"] == target_category
        ]
        self.tracker.init_model(
            queue_id,
            entry.category,
            total_prompts=len(filtered_prompts),
            model_metadata=model_entry,
        )

        status, completed_prompts, total = self.tracker.get_model_progress(queue_id)
        if self.skip_prehandled(idx, total_models, entry, status):
            return

        if entry.is_deferred_vision:
            self.log(f"\n[{idx}/{total_models}] {entry.requested_name} ({entry.category}) - Deferred (multimodal/vision)")
            self.tracker.skip_model(
                queue_id,
                "Multimodal/Vision model - deferred until real image assets exist",
                "deferred_vision",
            )
            self.tracker.save_status_to_file()
            return

        if entry.is_provider_unsupported:
            reason = entry.variant_note or "Provider unsupported"
            self.log(f"\n[{idx}/{total_models}] {entry.requested_name} ({entry.category}) - Unsupported: {reason[:80]}")
            self.tracker.skip_model(queue_id, reason, "provider_unsupported")
            self.tracker.save_status_to_file()
            return

        self.log(f"\n[{idx}/{total_models}] Evaluating {entry.requested_name} ({entry.resolved_runtime})")
        self.log(f"  Resolved ref: {entry.resolved_model_ref}")
        self.log(f"  Status: {status}, Completed prompts: {completed_prompts}/{total}")

        runtime_handle = self.acquire_runtime_fn(model_entry)
        if runtime_handle is None:
            error_msg = "Download/load failed"
            self.log(f"  ERROR: {error_msg}")
            self.tracker.fail_model(queue_id, error_msg)
            self.tracker.save_status_to_file()
            return

        try:
            self.run_prompts_for_model(
                model_entry=model_entry,
                runtime_handle=runtime_handle,
                target_category=target_category,
                filtered_prompts=filtered_prompts,
                status=status,
                completed_prompts=completed_prompts,
            )
        finally:
            self.cleanup_runtime_fn(runtime_handle)
            self.tracker.save_status_to_file()
            self.log("  Status saved to TEST_STATUS.md")
            self.log("\n" + "-" * 60)
            self.log(self.tracker.generate_status_report())

    def run_prompts_for_model(
        self,
        model_entry: dict[str, Any],
        runtime_handle: RuntimeHandle,
        target_category: str,
        filtered_prompts: list[dict[str, Any]],
        status: str,
        completed_prompts: int,
    ) -> None:
        entry = as_model_entry(model_entry)
        queue_id = entry.queue_id
        model_tag = runtime_handle.model_ref
        runtime_client = runtime_handle.runtime_client

        self.tracker.start_model(queue_id)
        run_benchmark, run_structured = self.runtime_adapters(
            runtime_handle, entry.resolved_runtime
        )

        model_results: list[dict[str, Any]] = []
        start_index = 0
        if status == "in_progress" and completed_prompts > 0:
            existing_csv = self.tracker.get_all_progress()["models"].get(queue_id, {}).get("csv_file")
            if existing_csv and os.path.exists(existing_csv):
                existing_results = self.store.load_existing_results(existing_csv)
                if existing_results:
                    model_results = existing_results
                    start_index = completed_prompts
                    self.log(f"  Resuming from prompt {start_index + 1}")

        self.log(f"  Running {len(filtered_prompts) - start_index} remaining prompts...")
        smoke_prompts = self.config.smoke_run_prompts if self.config.smoke_run_prompts > 0 else None
        loop_start_time = time.perf_counter()
        checkpoint_csv = None

        try:
            for i, prompt in enumerate(filtered_prompts):
                if i < start_index:
                    continue
                if smoke_prompts and (i - start_index) >= smoke_prompts:
                    self.log(f"\n  Smoke run: stopping after {smoke_prompts} prompts")
                    break

                if self.stop_for_slow_model(
                    i=i,
                    start_index=start_index,
                    queue_id=queue_id,
                    filtered_prompts=filtered_prompts,
                    model_results=model_results,
                    loop_start_time=loop_start_time,
                ):
                    return

                unified_data = self.benchmarker.benchmark_single(
                    model_tag, prompt, model_entry=model_entry
                )
                if run_benchmark is not None:
                    res = run_benchmark(
                        prompt["prompt"],
                        MAX_NEW_TOKENS,
                        is_vis=prompt.get("category", "") == "Multimodal Vision",
                        img_path=prompt.get("image_path"),
                    )
                    unified_data.update(
                        {
                            "tps": res.tps,
                            "ttft": res.ttft,
                            "latency": res.latency,
                            "output": res.content,
                            "error": res.error,
                        }
                    )

                if i < (start_index + self.config.phase2_limit):
                    self.add_structured_checks(
                        unified_data=unified_data,
                        prompt=prompt,
                        model_tag=model_tag,
                        target_category=target_category,
                        run_structured=run_structured,
                    )

                model_results.append(unified_data)
                checkpoint_csv = self.store.save_checkpoint_csv(model_results, queue_id)
                self.tracker.update_checkpoint(queue_id, i + 1, checkpoint_csv)

        except KeyboardInterrupt:
            self.save_interrupted(queue_id, model_results)
            raise
        except Exception as exc:
            self.save_failed(queue_id, model_results, str(exc))
            return

        self.finish_model(queue_id, model_results, checkpoint_csv)

    def runtime_adapters(
        self, runtime_handle: RuntimeHandle, resolved_runtime: str
    ) -> tuple[Callable[..., Any] | None, Callable[..., dict[str, Any]] | None]:
        model_tag = runtime_handle.model_ref
        runtime_client = runtime_handle.runtime_client
        if runtime_client is not None:
            self.log(f"  Using {resolved_runtime} runtime")

            def run_benchmark(prompt_text, max_tokens, is_vis=False, img_path=None):
                return runtime_client.generate_benchmark(
                    model_tag,
                    prompt_text,
                    max_tokens=max_tokens,
                    is_vision=is_vis,
                    image_path=img_path,
                )

            def run_structured(prompt_text, schema_json, temp, is_vis=False, img_path=None):
                content, error = runtime_client.generate_structured(
                    model_tag,
                    prompt_text,
                    schema_json,
                    temperature=temp,
                    is_vision=is_vis,
                    image_path=img_path,
                )
                return {
                    "success": error is None and len(content) > 0,
                    "error": error,
                    "output": content,
                }

            return run_benchmark, run_structured

        self.log("  Pre-loading model into GPU memory (Ollama)...")
        try:
            self.benchmarker.client.generate_benchmark(model_tag, "", max_tokens=1)
        except Exception:
            pass
        return None, None

    def add_structured_checks(
        self,
        unified_data: dict[str, Any],
        prompt: dict[str, Any],
        model_tag: str,
        target_category: str,
        run_structured: Callable[..., dict[str, Any]] | None,
    ) -> None:
        prompt_image_path = prompt.get("image_path")
        for temp in self.config.temps_to_test:
            if run_structured is not None:
                schema_class = get_schema_for_category(target_category)
                temp_res = run_structured(
                    prompt["prompt"],
                    schema_class.model_json_schema(),
                    temp,
                    is_vis=target_category == "Multimodal Vision",
                    img_path=prompt_image_path,
                )
            else:
                temp_res = self.structured_tester.generate_single_with_retry(
                    model_tag,
                    prompt["prompt"],
                    category=target_category,
                    temperature=temp,
                    image_path=prompt_image_path,
                )
            unified_data[f"temp_{temp}_success"] = temp_res["success"]
            unified_data[f"temp_{temp}_error"] = temp_res["error"]
            unified_data[f"temp_{temp}_output"] = temp_res["output"]

    def stop_for_slow_model(
        self,
        i: int,
        start_index: int,
        queue_id: str,
        filtered_prompts: list[dict[str, Any]],
        model_results: list[dict[str, Any]],
        loop_start_time: float,
    ) -> bool:
        prompts_done = i - start_index
        if prompts_done > 0:
            elapsed = time.perf_counter() - loop_start_time
            avg_time_per_prompt = elapsed / prompts_done
            prompts_left = len(filtered_prompts) - i
            eta_mins = (avg_time_per_prompt * prompts_left) / 60
            self.log(
                f"  Prompt {i + 1}/{len(filtered_prompts)} | Elapsed: {elapsed / 60:.1f}m | ETA: {eta_mins:.1f}m",
                end="\r",
            )
            if (
                self.config.slow_model_threshold_secs > 0
                and prompts_done >= 3
                and avg_time_per_prompt > self.config.slow_model_threshold_secs
            ):
                error = (
                    f"Average prompt time {avg_time_per_prompt:.0f}s > "
                    f"threshold {self.config.slow_model_threshold_secs}s"
                )
                self.log(f"\n  SLOW: {error}")
                if model_results:
                    checkpoint = self.store.save_checkpoint_csv(model_results, queue_id)
                    self.tracker.update_checkpoint(queue_id, len(model_results), checkpoint)
                self.tracker.fail_model(queue_id, error)
                return True
        else:
            self.log(
                f"  Prompt {i + 1}/{len(filtered_prompts)} | Calculating ETA...",
                end="\r",
            )
        return False

    def finish_model(
        self,
        queue_id: str,
        model_results: list[dict[str, Any]],
        checkpoint_csv: str | None,
    ) -> None:
        self.log(f"\n  Testing complete! ({len(model_results)} prompts)")
        error_count = sum(1 for result in model_results if result.get("error"))
        csv_path = self.save_unified_result(model_results, queue_id)

        if error_count == len(model_results) and model_results:
            sample_errors = [result["error"] for result in model_results if result.get("error")][:3]
            error_msg = f"All {len(model_results)} prompts failed. Sample: {'; '.join(sample_errors)}"
            self.log(f"  ERROR: {error_msg}")
            self.tracker.fail_model(queue_id, error_msg)
            self.log("  Marked as failed (all prompts errored)")
        else:
            self.tracker.complete_model(queue_id, csv_path)
            if error_count > 0:
                self.log(f"  Marked as completed ({error_count}/{len(model_results)} errors)")
            else:
                self.log("  Marked as completed")

        if checkpoint_csv and os.path.exists(checkpoint_csv) and checkpoint_csv != csv_path:
            try:
                os.remove(checkpoint_csv)
                self.log(f"  Cleaned up checkpoint: {os.path.basename(checkpoint_csv)}")
            except Exception:
                pass

    def save_unified_result(self, results_list: list[dict[str, Any]], model: str) -> str:
        csv_path = self.store.save_unified_result(results_list, model)
        self.log(f"Saved results for '{model}' to {csv_path}")
        return csv_path

    def save_interrupted(self, queue_id: str, model_results: list[dict[str, Any]]) -> None:
        self.log(f"\n  Interrupted! Saving checkpoint at prompt {len(model_results)}...")
        if model_results:
            csv_path = self.save_unified_result(model_results, queue_id)
            self.tracker.update_checkpoint(queue_id, len(model_results), csv_path)
        self.tracker.save_status_to_file()
        self.log("  Checkpoint saved. Run again to resume.")

    def save_failed(
        self, queue_id: str, model_results: list[dict[str, Any]], error_msg: str
    ) -> None:
        self.log(f"\n  ERROR during testing: {error_msg}")
        if model_results:
            csv_path = self.save_unified_result(model_results, queue_id)
            self.tracker.update_checkpoint(queue_id, len(model_results), csv_path)
        self.tracker.fail_model(queue_id, error_msg)
        self.tracker.save_status_to_file()

    def skip_prehandled(self, idx: int, total_models: int, entry: Any, status: str) -> bool:
        queue_id = entry.queue_id
        if status == "completed":
            self.log(
                f"\n[{idx}/{total_models}] {entry.requested_name} ({entry.category}) - Already completed, skipping"
            )
            return True
        if status == "failed":
            error = self.tracker.get_all_progress()["models"].get(queue_id, {}).get("error", "Unknown")
            self.log(
                f"\n[{idx}/{total_models}] {entry.requested_name} ({entry.category}) - Previously failed: {error[:80]}"
            )
            return True
        if status in ("skipped", "provider_unsupported", "deferred_vision"):
            reason = self.tracker.get_all_progress()["models"].get(queue_id, {}).get("error", "")
            self.log(
                f"\n[{idx}/{total_models}] {entry.requested_name} ({entry.category}) - Skipped: {reason[:80]}"
            )
            return True
        return False

    @staticmethod
    def target_category_for(model_category: str) -> str:
        return CATEGORY_PROMPT_MAP.get(model_category, "Multimodal Vision")


def run_project_pipeline() -> None:
    Phase1BenchmarkPass().run()
