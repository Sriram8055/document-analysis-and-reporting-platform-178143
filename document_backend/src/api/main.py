from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.db import init_db

app = FastAPI(
    title="Document Analysis Backend",
    description="Backend API for document upload, processing, entity extraction, mapping, and report generation.",
    version="0.1.0",
    openapi_tags=[
        {"name": "health", "description": "Service health and metadata"},
        {"name": "jobs", "description": "Job management and status"},
        {"name": "files", "description": "File management"},
        {"name": "results", "description": "Results and reports"},
        {"name": "ws", "description": "WebSocket realtime updates"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize database tables on application startup."""
    init_db()


@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Return a simple health status message.

    Returns:
        JSON object with health message.
    """
    return {"message": "Healthy"}
