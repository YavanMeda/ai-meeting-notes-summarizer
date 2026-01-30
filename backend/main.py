from fastapi import FastAPI

app = FastAPI(title="AI Meeting Notes Summarizer (Backend)")

@app.get("/")
def root():
    return {"status" : "ok"}