import time
import ollama
from dataclasses import dataclass
from typing import Optional

@dataclass
class BenchmarkResult:
    model: str
    tps: float
    ttft: float
    latency: float
    eval_count: int
    content: str
    error: Optional[str] = None

class OllamaClient:
    def __init__(self, host="http://localhost:11434"):
        # We can configure the host if needed, defaults to localhost
        pass

    def generate_benchmark(self, model: str, prompt: str, max_tokens: int = 128, is_vision: bool = False) -> BenchmarkResult:
        try:
            start_time = time.perf_counter()
            first_token_time = None
            
            message = {'role': 'user', 'content': prompt}
            if is_vision:
                # Provide a generic 1x1 PNG transparent pixel for baseline testing
                message['images'] = ["iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="]
            
            # Using streaming to capture TTFT
            stream = ollama.generate(
                model=model,
                prompt=prompt,
                images=message.get('images'),
                stream=True,
                options={"num_predict": max_tokens}
            )
            
            content_chunks = []
            
            for chunk in stream:
                if first_token_time is None:
                    first_token_time = time.perf_counter()
                content_chunks.append(chunk['response'])
                
                # The last chunk often contains the metrics if we simulate reading them,
                # but with python stream=True, the last chunk dict contains the metrics.
                if chunk.get('done'):
                    final_chunk = chunk
            
            end_time = time.perf_counter()
            
            if first_token_time is None:
                first_token_time = end_time  # Fallback if no tokens generated

            latency = end_time - start_time
            ttft = first_token_time - start_time
            
            # Extract metrics from final chunk
            eval_count = final_chunk.get('eval_count', 0)
            eval_duration_ns = final_chunk.get('eval_duration', 0)
            
            tps = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns > 0 else 0
            
            if tps == 0 and eval_count > 0:
                # Fallback TPS calculation
                tps = eval_count / (latency - ttft) if (latency - ttft) > 0 else 0

            return BenchmarkResult(
                model=model,
                tps=tps,
                ttft=ttft,
                latency=latency,
                eval_count=eval_count,
                content="".join(content_chunks)
            )

        except Exception as e:
            return BenchmarkResult(
                model=model,
                tps=0.0,
                ttft=0.0,
                latency=0.0,
                eval_count=0,
                content="",
                error=str(e)
            )

    def generate_structured(self, model: str, prompt: str, schema: dict, temperature: float = 0.0, is_vision: bool = False) -> tuple[str, Optional[str]]:
        try:
            message = {'role': 'user', 'content': prompt}
            if is_vision:
                message['images'] = ["iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="]
                
            response = ollama.chat(
                model=model,
                messages=[message],
                format=schema,
                options={'temperature': temperature}
            )
            return response.message.content, None
        except Exception as e:
            return "", str(e)
