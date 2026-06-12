"""
Unified Benchmark Orchestrator (Mega-Orchestrator)

Lifecycle: One-Pull, Three-Tests, One-Delete.
"""

import argparse
import os
import sys

if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["ANSI_COLORS_DISABLED"] = "1"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from rich.console import Console

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.phase_orchestration import PhaseOrchestrator


console = Console()


def log(msg, style=None):
    if style:
        console.print(f"[{style}]{msg}[/{style}]")
    else:
        console.print(msg)


def main(target_model=None):
    PhaseOrchestrator(log=log).run(target_model=target_model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mega-Orchestrator")
    parser.add_argument("--model", type=str, help="Filter to a specific model")
    args = parser.parse_args()
    main(target_model=args.model)
