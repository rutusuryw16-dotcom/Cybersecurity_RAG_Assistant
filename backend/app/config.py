import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "raw_logs"
KB_DIR = DATA_DIR / "knowledge_base"
VECTOR_DB_DIR = DATA_DIR / "vector_db"

# Ensure directories exist
for d in [DATA_DIR, LOGS_DIR, KB_DIR, VECTOR_DB_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Cloud-Based RAG Cybersecurity Incident Investigation Assistant"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Security & Auth
    SECRET_KEY: str = os.getenv("JWT_SECRET", "super-secret-cyber-soc-jwt-key-2026-very-secure")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Embedding & Vector DB
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHROMA_PERSIST_DIRECTORY: str = str(VECTOR_DB_DIR)
    SIMILARITY_TOP_K: int = 5
    CHUNK_SIZE: int = 400
    CHUNK_OVERLAP: int = 80
    
    # LLM Settings (Pluggable: local expert reasoning, or Gemini/OpenAI/Ollama)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "local")  # "local", "gemini", "openai", "ollama"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    
    # Cybersecurity Detection Thresholds
    BRUTE_FORCE_THRESHOLD: int = 5
    BRUTE_FORCE_WINDOW_SECONDS: int = 120
    PORT_SCAN_THRESHOLD: int = 8
    PORT_SCAN_WINDOW_SECONDS: int = 60
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    LOGS_DIR: Path = LOGS_DIR
    KB_DIR: Path = KB_DIR
    VECTOR_DB_DIR: Path = VECTOR_DB_DIR

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
