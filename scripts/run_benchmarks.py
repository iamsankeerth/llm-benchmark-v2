import os
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import warnings

warnings.filterwarnings("ignore")

if sys.platform == "win32":
    os.environ["ANSI_COLORS_DISABLED"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ.setdefault("OLLAMA_FLASH_ATTENTION", "1")

from src.phase1_pass import Phase1BenchmarkPass


def strip_ansi(text):
    if text is None:
        return ""
    ansi_pattern = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_pattern.sub("", text)


def log(msg, end=None, flush=False):
    if end:
        print(msg, end=end, flush=flush)
    else:
        print(msg)
    sys.stdout.flush()


def run_project_pipeline():
    Phase1BenchmarkPass(log=log).run()


if __name__ == "__main__":
    try:
        run_project_pipeline()
    except KeyboardInterrupt:
        log("\n\nPipeline interrupted. Run again to resume from last checkpoint.")
