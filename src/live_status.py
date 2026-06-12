"""Live benchmark status adapter.

FastAPI routes delegate here for process checks and stop control. Progress and
result shaping live behind ``ProgressProjection``.
"""

from __future__ import annotations

import subprocess
from typing import Any, Callable

import psutil

from src.artifact_store import BenchmarkArtifactStore
from src.progress_projection import (
    ProgressProjection,
    calc_eta as _calc_eta,
    calc_per_prompt_eta as _calc_per_prompt_eta,
    calc_total_model_eta as _calc_total_model_eta,
    detect_phase as _detect_phase,
    format_elapsed as _format_elapsed,
)


class SystemStatusAdapter:
    def __init__(self, store: BenchmarkArtifactStore):
        self.store = store

    def get_gpu_info(self) -> dict[str, str]:
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader",
                ],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(",")
                return {
                    "utilization": parts[0].strip(),
                    "vram_used": parts[1].strip(),
                    "vram_total": parts[2].strip(),
                }
        except Exception:
            pass
        return {"utilization": "N/A", "vram_used": "N/A", "vram_total": "N/A"}

    def get_benchmark_pid(self) -> int | None:
        if self.store.pid_file.exists():
            try:
                return int(self.store.pid_file.read_text().strip())
            except (ValueError, OSError):
                pass
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = proc.info.get("cmdline") or []
                cmdline_str = " ".join(cmdline)
                if "run_full_benchmark" in cmdline_str or "run_benchmarks" in cmdline_str:
                    if "python" in (proc.info.get("name") or "").lower():
                        return proc.info["pid"]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    @staticmethod
    def is_process_alive(pid: int) -> bool:
        return psutil.pid_exists(pid)

    @staticmethod
    def stop_process(pid: int) -> None:
        proc = psutil.Process(pid)
        try:
            proc.terminate()
            proc.wait(timeout=10)
        except psutil.TimeoutExpired:
            proc.kill()


class LiveStatusProjection:
    def __init__(
        self,
        store: BenchmarkArtifactStore | None = None,
        system: SystemStatusAdapter | None = None,
        queue_loader: Callable[[], list[dict[str, Any]]] | None = None,
        progress_projection: ProgressProjection | None = None,
    ):
        self.store = store or BenchmarkArtifactStore()
        self.system = system or SystemStatusAdapter(self.store)
        self.queue_loader = queue_loader or self._load_model_queue
        self.progress = progress_projection or ProgressProjection(
            store=self.store,
            queue_loader=self.queue_loader,
        )

    @staticmethod
    def _load_model_queue() -> list[dict[str, Any]]:
        try:
            from src.model_queue import build_model_queue

            return build_model_queue()
        except Exception:
            return []

    def status_payload(self) -> dict[str, Any]:
        pid = self.system.get_benchmark_pid()
        alive = self.system.is_process_alive(pid) if pid else False
        return self.progress.live_payload(
            process_alive=alive,
            process_pid=pid,
            gpu=self.system.get_gpu_info(),
            log_tail=self.store.read_log_tail(30),
            progress=self.store.load_progress(),
            queue=self.queue_loader(),
        )

    def model_prompts_payload(self, queue_id: str) -> dict[str, Any] | None:
        return self.store.model_prompts(queue_id)

    def stop_pipeline(self) -> dict[str, Any]:
        pid = self.system.get_benchmark_pid()
        if not pid:
            raise LookupError("No benchmark process found")
        if not self.system.is_process_alive(pid):
            raise LookupError(f"Process {pid} is not running")
        self.system.stop_process(pid)
        return {"stopped": True, "pid": pid}
