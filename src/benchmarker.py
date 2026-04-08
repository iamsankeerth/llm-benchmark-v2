import os
import time
from datetime import datetime
import pandas as pd
from src.ollama_client import OllamaClient
from src.gpu_monitor import GPUMonitor

class Benchmarker:
    def __init__(self):
        self.client = OllamaClient()

    def benchmark_single(self, model: str, prompt_data: dict) -> dict:
        """
        Phase 1: Run a single prompt to measure TPS, TTFT, Latency, and Peak VRAM.
        """
        with GPUMonitor() as monitor:
            is_vis = (prompt_data.get("category") == "Multimodal Vision")
            from config import MAX_NEW_TOKENS
            res = self.client.generate_benchmark(model, prompt_data["prompt"], max_tokens=MAX_NEW_TOKENS, is_vision=is_vis)
            peak_vram = monitor.peak_vram

        return {
            "model": model,
            "prompt_id": prompt_data.get("id"),
            "category": prompt_data["category"],
            "tps": res.tps,
            "ttft": res.ttft,
            "latency": res.latency,
            "peak_vram_mb": peak_vram,
            "error": res.error
        }
