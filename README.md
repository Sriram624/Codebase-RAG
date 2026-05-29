# Codebase RAG Assistant

Ask questions about a local codebase using retrieval-augmented generation (RAG). This app ingests a repo, builds embeddings in Postgres/pgvector, and serves a FastAPI backend with a Streamlit chat UI.

## What It Does

- Ingests a codebase from `data/your-repo`
- Splits code into AST-based chunks
- Stores embeddings in Postgres with pgvector
- Answers questions via an Ollama-hosted model

## Architecture

- `backend/main.py` FastAPI API (`/query`, `/health`, `/ollama-health`)
- `backend/graph.py` LangGraph pipeline (classify → retrieve → compress → generate)
- `backend/ingestion.py` indexing pipeline using LlamaIndex + PGVector
- `backend/streamlit_app.py` Streamlit UI

## Prerequisites

- Docker Desktop (running)
- Ollama installed and running on the host
- A local code repo mounted at `./data/your-repo`

## Quick Start (Docker)

1. Put a repo under `data/your-repo` (or replace with your own path).
2. Start services:

```powershell
docker-compose up -d
```

3. Open the UI:

```powershell
streamlit run backend\streamlit_app.py
```

- Backend runs at `http://localhost:8000`
- UI runs at `http://localhost:8501`

## Configuration

Set these in `docker-compose.yml` or your environment:

- `OLLAMA_MODEL` (default: `qwen2.5:7b`)
- `EMBED_MODEL` (default: `nomic-ai/nomic-embed-text-v1.5`)
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`

See `backend/config.py` for defaults.

## Data Ingestion

The backend ingests from `data/your-repo` at startup. If it does not exist, startup fails. Create the folder and add code before running.

## Troubleshooting

### Backend not running

- Check Docker Desktop is running.
- Check for port conflicts:

```powershell
netstat -ano | findstr :5432
netstat -ano | findstr :8000
```

If `5432` is in use, change `docker-compose.yml` to map another host port (e.g., `5434:5432`).

### Ollama not reachable

The backend uses `http://host.docker.internal:11434` to reach Ollama from Docker.

Test health:

```powershell
curl http://localhost:8000/ollama-health
```

### Model memory errors

If you see:

```
model requires more system memory
```

Switch to a smaller model via `OLLAMA_MODEL` in `docker-compose.yml`.

### Tree-sitter errors

This repo uses `tree-sitter` and `tree-sitter-languages` directly in `backend/ingestion.py` to avoid `tree_sitter_language_pack` compatibility issues.

## Useful Commands

```powershell
docker-compose logs -f backend
```

```powershell
docker-compose down -v
```

## Notes

- First run may take a while to download embedding and LLM models.
- For Linux, `host.docker.internal` may require manual setup. If so, replace the Ollama host with the Docker gateway IP.

