from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.ollama_client import OllamaClient
from config import CORE_MODELS

router = APIRouter()
client = OllamaClient()

class RequestPayload(BaseModel):
    prompt: str
    model_type: str = "chat" # chat, reasoning, coding
    max_tokens: int = 512

class BenchmarkResponse(BaseModel):
    model: str
    tps: float
    ttft: float
    latency: float
    content: str
    error: str | None

@router.get("/models")
def get_models():
    return CORE_MODELS

@router.post("/generate", response_model=BenchmarkResponse)
def generate_response(payload: RequestPayload):
    if payload.model_type not in CORE_MODELS:
        raise HTTPException(status_code=400, detail="Invalid model_type. Must be chat, reasoning, or coding")
    
    model_tag = CORE_MODELS[payload.model_type]
    result = client.generate_benchmark(model_tag, payload.prompt, payload.max_tokens)
    
    if result.error:
        raise HTTPException(status_code=500, detail=result.error)
        
    return BenchmarkResponse(
        model=result.model,
        tps=result.tps,
        ttft=result.ttft,
        latency=result.latency,
        content=result.content,
        error=result.error
    )
