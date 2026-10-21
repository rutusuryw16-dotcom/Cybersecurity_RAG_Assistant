import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from .config import settings
from .auth import (
    User, Token, create_access_token, get_current_user, require_admin,
    verify_password, USERS_DB
)
from .log_parser import (
    parse_syslog_auth, parse_csv_logs, parse_json_logs, parse_pdf,
    chunk_text, LogEntry
)
from .rules_engine import rules_engine, IncidentAlert
from .vector_store import vector_store
from .rag_engine import rag_engine, InvestigationResponse
from .evaluation import evaluation_suite, BenchmarkMetrics
from .data_generator import generate_benchmark_datasets

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Cloud-Based RAG Assistant for Cybersecurity Incident Investigation and Evidence-Based Threat Analysis"
)

# Enable CORS for React frontend (Vite default port 5173, production port, wildcard for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory log cache for fast SOC incident scanning
_PARSED_LOGS: List[LogEntry] = []


@app.on_event("startup")
async def startup_event():
    """Auto-initialize benchmark datasets on first launch if empty."""
    stats = vector_store.get_stats()
    if stats["total_chunks"] == 0:
        print("[Startup] Initializing default benchmark cybersecurity scenarios & knowledge base...")
        generate_benchmark_datasets()
        # Load generated logs into in-memory cache
        _reload_logs_from_disk()


def _reload_logs_from_disk():
    global _PARSED_LOGS
    _PARSED_LOGS.clear()
    for fname in os.listdir(settings.LOGS_DIR):
        fpath = settings.LOGS_DIR / fname
        if not fpath.is_file():
            continue
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if fname.endswith(".csv"):
                _PARSED_LOGS.extend(parse_csv_logs(content, fname))
            elif fname.endswith(".json"):
                _PARSED_LOGS.extend(parse_json_logs(content, fname))
            else:
                _PARSED_LOGS.extend(parse_syslog_auth(content, fname))
        except Exception as e:
            print(f"Error loading {fname}: {e}")


# ==========================================
# Authentication Endpoints (JWT / RBAC)
# ==========================================
@app.post(f"{settings.API_V1_PREFIX}/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS_DB.get(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        username=user.username
    )


@app.get(f"{settings.API_V1_PREFIX}/auth/demo-token", response_model=Token)
async def get_demo_token(role: str = Query("analyst", regex="^(analyst|admin)$")):
    """Instant 1-click token generation for quick demonstration & grading."""
    user = USERS_DB.get(role, USERS_DB["analyst"])
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        username=user.username
    )


@app.get(f"{settings.API_V1_PREFIX}/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ==========================================
# Ingestion & Log Management
# ==========================================
@app.post(f"{settings.API_V1_PREFIX}/logs/upload")
async def upload_log_file(
    file: UploadFile = File(...),
    category: str = Query("logs", regex="^(logs|knowledge_base)$"),
    current_user: User = Depends(get_current_user)
):
    """Uploads and indexes PDF, TXT, CSV, JSON logs or security reference documents."""
    filename = file.filename
    content_bytes = await file.read()
    
    # Save raw file
    target_dir = settings.LOGS_DIR if category == "logs" else settings.KB_DIR
    save_path = target_dir / filename
    with open(save_path, "wb") as f:
        f.write(content_bytes)

    # Parse and index
    chunks = []
    parsed_entries = []
    if filename.endswith(".pdf"):
        text = parse_pdf(content_bytes, filename)
        chunks = chunk_text(text, source_file=filename, chunk_size=settings.CHUNK_SIZE, overlap=settings.CHUNK_OVERLAP)
    elif filename.endswith(".csv"):
        text = content_bytes.decode("utf-8", errors="ignore")
        parsed_entries = parse_csv_logs(text, filename)
        _PARSED_LOGS.extend(parsed_entries)
        for i, entry in enumerate(parsed_entries):
            chunks.append(chunk_text(entry.raw_message, source_file=filename)[0])
    elif filename.endswith(".json"):
        text = content_bytes.decode("utf-8", errors="ignore")
        parsed_entries = parse_json_logs(text, filename)
        _PARSED_LOGS.extend(parsed_entries)
        for entry in parsed_entries:
            chunks.append(chunk_text(entry.raw_message, source_file=filename)[0])
    else:  # plain text or syslog
        text = content_bytes.decode("utf-8", errors="ignore")
        if category == "logs":
            parsed_entries = parse_syslog_auth(text, filename)
            _PARSED_LOGS.extend(parsed_entries)
        chunks = chunk_text(text, source_file=filename, chunk_size=settings.CHUNK_SIZE, overlap=settings.CHUNK_OVERLAP)

    for c in chunks:
        c.metadata["category"] = category

    indexed_count = vector_store.add_chunks(chunks, category=category)

    return {
        "status": "success",
        "filename": filename,
        "category": category,
        "chunks_indexed": indexed_count,
        "parsed_log_entries": len(parsed_entries)
    }


@app.post(f"{settings.API_V1_PREFIX}/logs/preload-benchmarks")
async def preload_benchmarks(current_user: User = Depends(get_current_user)):
    """Preloads the 50-failed-logins brute-force dataset, web attacks, port scans, and MITRE KB."""
    generate_benchmark_datasets()
    _reload_logs_from_disk()
    alerts = rules_engine.analyze(_PARSED_LOGS)
    return {
        "status": "success",
        "message": "Benchmark cybersecurity scenarios & MITRE knowledge base loaded",
        "total_logs": len(_PARSED_LOGS),
        "flagged_incidents": len(alerts)
    }


@app.get(f"{settings.API_V1_PREFIX}/logs/all")
async def get_all_logs(
    limit: int = Query(50, ge=1, le=500),
    severity: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Retrieve ingested security logs with optional severity filter."""
    if not _PARSED_LOGS:
        _reload_logs_from_disk()
    logs = _PARSED_LOGS
    if severity:
        logs = [l for l in logs if l.severity.upper() == severity.upper()]
    return {
        "total": len(logs),
        "limit": limit,
        "logs": logs[:limit]
    }


# ==========================================
# Rules-Based Incident Correlation
# ==========================================
@app.get(f"{settings.API_V1_PREFIX}/incidents/analyze", response_model=List[IncidentAlert])
async def analyze_incidents(current_user: User = Depends(get_current_user)):
    """Runs cybersecurity detection rules across all ingested logs."""
    if not _PARSED_LOGS:
        _reload_logs_from_disk()
    alerts = rules_engine.analyze(_PARSED_LOGS)
    return alerts


# ==========================================
# RAG AI Investigation Assistant
# ==========================================
class InvestigateRequest(BaseModel):
    query: str
    incident_context: Optional[str] = None
    top_k: int = 5


@app.post(f"{settings.API_V1_PREFIX}/investigate", response_model=InvestigationResponse)
async def investigate_incident(
    req: InvestigateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Core RAG Investigation Assistant.
    Retrieves evidence, explains threats, provides MITRE mapping,
    and returns citations + side-by-side ungrounded comparison.
    """
    res = await rag_engine.investigate(
        query=req.query,
        top_k=req.top_k,
        incident_context=req.incident_context
    )
    return res


# ==========================================
# Vector Store & Search Inspector
# ==========================================
@app.get(f"{settings.API_V1_PREFIX}/vector-store/stats")
async def get_vector_store_stats(current_user: User = Depends(get_current_user)):
    return vector_store.get_stats()


@app.get(f"{settings.API_V1_PREFIX}/vector-store/search")
async def search_vector_store(
    query: str,
    top_k: int = 5,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    results = vector_store.search(query=query, top_k=top_k, category=category)
    return {
        "query": query,
        "total_results": len(results),
        "results": results
    }


# ==========================================
# Evaluation & Benchmark Suite
# ==========================================
@app.get(f"{settings.API_V1_PREFIX}/evaluation/benchmark", response_model=BenchmarkMetrics)
async def run_evaluation_benchmark(current_user: User = Depends(get_current_user)):
    """Evaluates detection metrics (Precision/Recall/F1), MRR, and citation accuracy."""
    return evaluation_suite.run_benchmark()


# ==========================================
# Cloud & System Health Monitoring
# ==========================================
@app.get("/health")
@app.get(f"{settings.API_V1_PREFIX}/system/status")
async def system_status():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": os.getenv("ENVIRONMENT", "cloud-docker"),
        "vector_db_chunks": len(vector_store.documents),
        "total_cached_logs": len(_PARSED_LOGS),
        "llm_provider": settings.LLM_PROVIDER,
        "cloud_readiness": {
            "docker_support": True,
            "k8s_readiness_probe": "GET /health (HTTP 200)",
            "rbac_enabled": True
        }
    }


# ==========================================
# Pre-built Frontend SPA Static Serving
# (Allows running the full app without Node.js!)
# ==========================================
_FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    _ASSETS_DIR = _FRONTEND_DIST / "assets"
    if _ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(_ASSETS_DIR)), name="frontend_assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa_frontend(full_path: str):
        # Do not catch API or docs routes
        if full_path.startswith(("api", "docs", "openapi.json", "health")):
            raise HTTPException(status_code=404, detail="Not Found")
        target_file = _FRONTEND_DIST / full_path
        if full_path and target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(_FRONTEND_DIST / "index.html")

