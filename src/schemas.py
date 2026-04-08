from pydantic import BaseModel, Field
from typing import Optional

class SentimentAnalysis(BaseModel):
    text: str = Field(description="The source text analyzed")
    sentiment: str = Field(description="Sentiment, literally 'positive', 'negative', or 'neutral'")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    key_phrases: list[str] = Field(description="Key phrases extracted from text")

class CodeReview(BaseModel):
    code_summary: str = Field(description="What the code does")
    bugs_found: list[str] = Field(description="List of bugs found")
    overall_quality: str = Field(description="One of: 'excellent', 'good', 'fair', 'poor'")
    lines_of_code: Optional[int] = Field(description="Approximate lines of code", default=None)

class ReasoningResponse(BaseModel):
    conclusion: str = Field(description="Final conclusion or answer")
    reasoning_steps: list[str] = Field(description="Step-by-step reasoning process")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the answer")
    evidence: list[str] = Field(description="Supporting evidence or references")

class CreativeWriting(BaseModel):
    title: str = Field(description="Title of the creative piece")
    content: str = Field(description="The written content")
    word_count: int = Field(ge=0, description="Number of words")
    style_elements: list[str] = Field(description="Style elements used")

class ImageAnalysis(BaseModel):
    description: str = Field(description="Description of the image")
    detected_objects: list[str] = Field(description="Objects detected in the image")
    anomaly_score: float = Field(ge=0.0, le=1.0, description="Anomaly score if applicable")
    recommendations: list[str] = Field(description="Recommendations or observations")

SCHEMAS = {
    "SentimentAnalysis": SentimentAnalysis,
    "CodeReview": CodeReview,
    "ReasoningResponse": ReasoningResponse,
    "CreativeWriting": CreativeWriting,
    "ImageAnalysis": ImageAnalysis,
}

def get_schema_for_category(category: str):
    """Get the appropriate schema for a given category."""
    mapping = {
        "Coding Generation": CodeReview,
        "Medium Reasoning": ReasoningResponse,
        "Chat & Generation": CreativeWriting,
        "Multimodal Vision": ImageAnalysis,
    }
    return mapping.get(category, SentimentAnalysis)
