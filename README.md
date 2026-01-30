# AI Meeting Notes Summarizer

A full-stack application that demonstrates **React**, **FastAPI**, and **GenAI API integration**.
The system accepts raw meeting transcripts and returns **structured meeting notes** (summary, decisions, action items, risks, and open questions) via a schema-validated backend API.

The project is intentionally designed to emphasize **clean architecture, strict API contracts, and safe GenAI integration**, rather than model quality.

---

## Architecture Overview

```
React (Vite)
  ↓ HTTP (JSON)
FastAPI (Pydantic validation)
  ↓
OpenAI API (gpt-4o-mini, structured output)
```

### Key design principles

* **Frontend / backend separation**
* **Strict request & response schemas**
* **Schema-constrained GenAI output**
* **Secrets handled via environment variables**
* **Frontend unchanged when AI logic is swapped**

---

## Tech Stack

### Frontend

* React
* Vite
* Fetch API

### Backend

* Python 3.12
* FastAPI
* Pydantic
* Uvicorn
* `python-dotenv`

### GenAI

* OpenAI Responses API
* Model: `gpt-4o-mini`
* JSON Schema–enforced structured output

---

## Features

* Paste meeting transcripts in the browser
* Backend validates input via Pydantic
* GenAI produces **structured JSON**, not free-form text
* Action items include optional owner, due date, priority, and source quote
* Frontend renders all sections deterministically
* Identical output from backend `/docs` and frontend UI

---

## API Contract

### Endpoint

```
POST /summarize
```

### Request

```json
{
  "transcript": "string (non-empty)"
}
```

### Response (simplified)

```json
{
  "meeting_title": "string",
  "summary_bullets": ["string"],
  "decisions": ["string"],
  "action_items": [
    {
      "task": "string",
      "owner": "string | null",
      "due_date": "string | null",
      "priority": "low | medium | high",
      "source_quote": "string | null"
    }
  ],
  "risks_blockers": ["string"],
  "open_questions": ["string"]
}
```

The response shape is enforced twice:

1. **At generation time** via JSON Schema
2. **At runtime** via Pydantic validation

---

## Running Locally

### Prerequisites

* Node.js (18+)
* Python 3.12
* An OpenAI API key

---

### Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
OPENAI_API_KEY=sk-...
```

Run the backend:

```bash
uvicorn main:app --reload
```

Backend will be available at:

```
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

---

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at:

```
http://localhost:5173
```

---

## Testing

### Backend (recommended first)

* Open `http://127.0.0.1:8000/docs`
* Use **POST /summarize**
* Paste a transcript (single-line or escaped `\n`)

### Frontend

* Paste the same transcript into the UI
* Click **Summarize**
* Confirm identical structured output

---

## Security Notes

* API keys are stored **only** in `.env`
* `.env` is ignored by Git
* Secrets are never exposed to the frontend
* Backend fails fast if the key is missing

---

## Why `gpt-4o-mini`?

The goal of this project is to demonstrate:

* correct GenAI API usage
* structured output enforcement
* system integration

Model quality beyond “it works” is intentionally out of scope.
The model can be swapped without changing the frontend or API contract.

---

## Project Scope (Intentional)

This project **does not** focus on:

* advanced prompt tuning
* model benchmarking
* UI polish
* long-term storage
* authentication

It focuses on **engineering fundamentals**:

* correctness
* validation
* architecture
* integration

---

## Possible Extensions

* Toggle between stub / AI mode
* Export summaries as Markdown or PDF
* Persist summaries
* Add tests
* Add authentication
* Support multiple models

---


