from typing import List, Optional, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from pathlib import Path
import os

import json

from openai import OpenAI
MODEL_NAME = "gpt-4o-mini"

dotenv_path = Path(__file__).with_name(".env")
print("Loading .env from:", dotenv_path)
print(".env exists:", dotenv_path.exists())

load_dotenv(dotenv_path=dotenv_path)

print("OPENAI_API_KEY present:", bool(os.getenv("OPENAI_API_KEY")))

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

client = OpenAI()

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


SUMMARY_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "meeting_title": {"type": "string"},
        "summary_bullets": {"type": "array", "items": {"type": "string"}},
        "decisions": {"type": "array", "items": {"type": "string"}},
        "action_items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "task": {"type": "string"},
                    "owner": {"type": ["string", "null"]},
                    "due_date": {"type": ["string", "null"]},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                    "source_quote": {"type": ["string", "null"]},
                },
                "required": ["task", "owner", "due_date", "priority", "source_quote"],
            },
        },
        "risks_blockers": {"type": "array", "items": {"type": "string"}},
        "open_questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "meeting_title",
        "summary_bullets",
        "decisions",
        "action_items",
        "risks_blockers",
        "open_questions",
    ],
}


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
    import json

    system_prompt = (
    "You are a meeting notes assistant.\n"
    "Return ONLY valid JSON that matches the provided schema.\n"
    "Rules:\n"
    "- Only use information explicitly present in the transcript.\n"
    "- Do not guess names, dates, or decisions.\n"
    "- If an owner or due date is not stated, use null.\n"
    "- Keep summary bullets short.\n"
    "- Priority must be one of: low, medium, high.\n"
    "- source_quote should be a short supporting quote from the transcript, or null.\n"
    )

    try:
        resp = client.responses.create(
            model=MODEL_NAME,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.transcript},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "meeting_summary",
                    "strict": True,
                    "schema": SUMMARY_SCHEMA,
                }
            },
            max_output_tokens=700,
        )

        data = json.loads(resp.output_text)
        return SummarizeResponse.model_validate(data)

    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="Model returned invalid JSON.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI summarization failed: {str(e)}")


