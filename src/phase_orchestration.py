"""Full benchmark phase orchestration."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from config import MODEL_QUEUE
from src.artifact_store import BenchmarkArtifactStore
from src.lifecycle import delete_ollama_tag, pull_ollama_tag
from src.model_comparator import ModelComparator
from src.model_entry import as_model_entry
from src.runtime_capability import needs_orchestrated_ollama_lifecycle


LogFn = Callable[..., None]


@dataclass(frozen=True)
class BenchmarkPhase:
    script_name: str
    display_name: str


DEFAULT_PHASES = (
    BenchmarkPhase("run_benchmarks.py", "Test A: Phase 1 (CSV Data)"),
    BenchmarkPhase("run_llama_bench.py", "Test B: llama-bench (Decode Speed)"),
    BenchmarkPhase("run_promptfoo.py", "Test C: promptfoo (Quality Eval)"),
)


class SubprocessPhaseAdapter:
    def __init__(
        self,
        scripts_dir: str | Path | None = None,
        python_exe: str | None = None,
        log: LogFn | None = None,
    ):
        self.scripts_dir = Path(scripts_dir) if scripts_dir else Path(__file__).parent.parent / "scripts"
        self.python_exe = python_exe or sys.executable
        self.log = log or print

    def run(self, phase: BenchmarkPhase) -> None:
        self._log(f"\n[bold magenta]--- Running {phase.display_name} ---[/bold magenta]")
        script_path = self.scripts_dir / phase.script_name
        try:
            subprocess.run([self.python_exe, str(script_path)], check=True)
        except subprocess.CalledProcessError as exc:
            self._log(f"[red]X Error during {phase.display_name}: {exc}[/red]")

    def _log(self, msg: str, style: str | None = None) -> None:
        try:
            self.log(msg, style=style)
        except TypeError:
            self.log(msg)


class PhaseOrchestrator:
    """Owns one-pull, three-tests, one-delete orchestration."""

    def __init__(
        self,
        model_queue: list[dict[str, Any]] | None = None,
        store: BenchmarkArtifactStore | None = None,
        phases: tuple[BenchmarkPhase, ...] = DEFAULT_PHASES,
        phase_adapter: SubprocessPhaseAdapter | None = None,
        log: LogFn | None = None,
        env: dict[str, str] | None = None,
    ):
        self.model_queue = model_queue or MODEL_QUEUE
        self.store = store or BenchmarkArtifactStore()
        self.phases = phases
        self.log = log or print
        self.phase_adapter = phase_adapter or SubprocessPhaseAdapter(log=self.log)
        self.env = env if env is not None else os.environ

    def run(self, target_model: str | None = None) -> None:
        self._log(
            "\n[bold cyan]"
            + "=" * 60
            + "\n MEGA-ORCHESTRATOR: ONE-PULL, THREE-TESTS, ONE-DELETE\n"
            + "=" * 60
            + "[/bold cyan]"
        )

        eligible = self.eligible_models(target_model)
        self._log(f"Found {len(eligible)} models to test.\n")

        old_skip = self.env.get("BENCHMARK_SKIP_LIFECYCLE")
        old_single = self.env.get("BENCHMARK_SINGLE_MODEL")
        self.env["BENCHMARK_SKIP_LIFECYCLE"] = "1"

        try:
            for idx, model in enumerate(eligible, 1):
                self.run_model(idx, len(eligible), model)
            self.generate_report()
        finally:
            self.restore_env("BENCHMARK_SKIP_LIFECYCLE", old_skip)
            self.restore_env("BENCHMARK_SINGLE_MODEL", old_single)

    def eligible_models(self, target_model: str | None = None) -> list[dict[str, Any]]:
        eligible = []
        for model in self.model_queue:
            entry = as_model_entry(model)
            if entry.status not in ("pending", "in_progress"):
                continue
            if not needs_orchestrated_ollama_lifecycle(model):
                continue
            if target_model and target_model.lower() not in entry.requested_name.lower():
                continue
            eligible.append(model)
        return eligible

    def run_model(self, idx: int, total: int, model: dict[str, Any]) -> None:
        entry = as_model_entry(model)
        name = entry.requested_name
        queue_id = entry.queue_id
        tag = entry.ollama_tag

        if not tag:
            self._log(f"[yellow]Skipping {name} (no ollama_tag)[/yellow]")
            return

        if self.all_phases_done(model):
            self._log(f"\n[{idx}/{total}] {name} - All phases complete, skipping")
            return

        self._log(f"\n[bold white on blue] MODEL {idx}/{total}: {name} ({tag}) [/bold white on blue]")
        self.env["BENCHMARK_SINGLE_MODEL"] = queue_id

        if not self.download_model(tag):
            return

        try:
            for phase in self.phases:
                self.phase_adapter.run(phase)
        finally:
            self.delete_model(tag)

    def download_model(self, ollama_tag: str) -> bool:
        self._log(f"\n[bold blue]>>> Downloading {ollama_tag}...[/bold blue]")
        return pull_ollama_tag(ollama_tag, log=self._log)

    def delete_model(self, ollama_tag: str) -> None:
        self._log(f"\n[bold blue]>>> Deleting {ollama_tag} to free up space...[/bold blue]")
        delete_ollama_tag(ollama_tag, log=self._log)

    def all_phases_done(self, model_entry: dict[str, Any]) -> bool:
        return self.store.all_phases_done(model_entry)

    def generate_report(self) -> None:
        self._log(
            "\n[bold cyan]"
            + "=" * 60
            + "\n FINAL STEP: GENERATING DASHBOARD REPORT\n"
            + "=" * 60
            + "[/bold cyan]"
        )
        self.env.pop("BENCHMARK_SINGLE_MODEL", None)
        ModelComparator().run_offline_report()

    def restore_env(self, name: str, old_value: str | None) -> None:
        if old_value is None:
            self.env.pop(name, None)
        else:
            self.env[name] = old_value

    def _log(self, msg: str, style: str | None = None) -> None:
        try:
            self.log(msg, style=style)
        except TypeError:
            self.log(msg)


def run_full_benchmark(target_model: str | None = None, log: LogFn | None = None) -> None:
    PhaseOrchestrator(log=log).run(target_model=target_model)
