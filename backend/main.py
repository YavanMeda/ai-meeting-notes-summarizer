from typing import List, Optional, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Meeting Notes Summarizer (Backend)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Request / Response Schemas
# -----------------------

class SummarizeRequest(BaseModel):
    transcript: str = Field(..., min_length=1, max_length=50_000)


class ActionItem(BaseModel):
    task: str = Field(..., min_length=1, max_length=300)
    owner: Optional[str] = Field(default=None, max_length=100)
    due_date: Optional[str] = Field(
        default=None,
        description="YYYY-MM-DD if explicitly stated"
    )
    priority: Literal["low", "medium", "high"] = "medium"
    source_quote: Optional[str] = Field(default=None, max_length=300)


class SummarizeResponse(BaseModel):
    meeting_title: str
    summary_bullets: List[str]
    decisions: List[str]
    action_items: List[ActionItem]
    risks_blockers: List[str]
    open_questions: List[str]


# -----------------------
# Endpoints
# -----------------------

@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest) -> SummarizeResponse:
    # Defensive check (min_length already prevents empty strings, but whitespace-only is possible)
    if not req.transcript.strip():
        raise HTTPException(status_code=422, detail="Transcript cannot be blank.")

    # Stub response (no AI yet)
    return SummarizeResponse(
        meeting_title="Untitled meeting",
        summary_bullets=[
            "Placeholder summary bullet (AI will replace this later)."
        ],
        decisions=[],
        action_items=[
            ActionItem(
                task="Send meeting notes to attendees",
                owner=None,
                due_date=None,
                priority="medium",
                source_quote=None,
            )
        ],
        risks_blockers=[],
        open_questions=[],
    )
