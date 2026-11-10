"""REST API for the summarizer (FastAPI).

Run with:  uvicorn api:app --port 8000
Docs at:   http://localhost:8000/docs
"""

from typing import List, Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

import storage
from models.summarizer import TextSummarizer
from utils.text_processor import TextProcessor

app = FastAPI(title="Terms & Conditions Summarizer API", version="1.0.0")

summarizer = TextSummarizer()
text_processor = TextProcessor()

ModelName = Literal["legal", "bart", "t5", "lexrank", "luhn", "lsa"]


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Document text to summarize")
    model: ModelName = "legal"
    sentences: int = Field(3, ge=1, le=10, description="Target summary length in sentences")


class SummarizeResponse(BaseModel):
    id: int
    summary: str
    key_points: List[str]
    model: str
    original_words: int
    summary_words: int
    compression_ratio: float
    processing_time: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest):
    text = text_processor.preprocess(req.text)
    original_words = len(text.split())
    if original_words < 10:
        raise HTTPException(status_code=422, detail="Text must contain at least 10 words.")

    result = summarizer.generate_summary(text=text, max_length=req.sentences, model_type=req.model)
    summary_words = len(result["summary"].split())
    record_id = storage.save_summary(
        source="api",
        model=req.model,
        original_words=original_words,
        summary_words=summary_words,
        processing_time=result["processing_time"],
        summary=result["summary"],
    )
    return SummarizeResponse(
        id=record_id,
        summary=result["summary"],
        key_points=result.get("key_points", []),
        model=req.model,
        original_words=original_words,
        summary_words=summary_words,
        compression_ratio=round((1 - summary_words / original_words) * 100, 1),
        processing_time=result["processing_time"],
    )


@app.get("/api/v1/history")
def history(limit: int = Query(20, ge=1, le=100)):
    return storage.recent_summaries(limit=limit)


@app.get("/api/v1/stats")
def stats():
    return storage.usage_by_model()
