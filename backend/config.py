import os

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-ai/nomic-embed-text-v1.5")

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "code_rag_pro_db")
