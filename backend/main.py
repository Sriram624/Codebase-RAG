# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from ingestion import ingest_codebase
from graph import build_graph
import uvicorn
from config import *

app = FastAPI(title="Codebase RAG Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

index = None
graph = None

class Query(BaseModel):
    question: str
    chat_history: list = Field(default_factory=list)

def _normalize_history(history: list) -> list:
    """Convert chat history to string format for LLM processing"""
    normalized = []
    for item in history:
        if isinstance(item, dict):
            role = item.get("role", "user")
            content = item.get("content", "")
            normalized.append(f"{role}: {content}")
        else:
            normalized.append(str(item))
    return normalized

@app.on_event("startup")
async def startup():
    global index, graph
    try:
        repo_path = "/app/data/your-repo"
        index = ingest_codebase(repo_path)
        graph = build_graph(index)
        print("🚀 Codebase RAG Backend Started Successfully")
    except Exception as e:
        print(f"❌ Startup Error: {e}")
        raise

@app.post("/query")
async def query(q: Query):
    try:
        inputs = {
            "question": q.question,
            "intent": "",
            "context": [],
            "compressed_context": "",
            "answer": "",
            "steps": [],
            "chat_history": _normalize_history(q.chat_history),
        }
        result = await graph.ainvoke(inputs)
        return {"answer": result["answer"], "steps": result["steps"]}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "error": "error processing the query",
            "details": str(e),
            "answer": "Error processing query",
            "steps": []
        }
@app.get("/ollama-health")
def check_ollama():
    import requests
    try:
        # Update URL if you use a different host/port in your config
        url = "http://host.docker.internal:11434/"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return {"status": "connected", "response": response.text}
        return {"status": "error", "code": response.status_code}
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}


@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
