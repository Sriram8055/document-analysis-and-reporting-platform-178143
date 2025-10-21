from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings

app = FastAPI(
    title="Document Analysis and Reporting Backend",
    description="Backend API for document upload, processing, entity extraction, mapping, and report generation.",
    version="0.1.0",
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PUBLIC_INTERFACE
@app.get("/", summary="Health Check", tags=["meta"])
def health_check():
    """Health check endpoint to verify service is running."""
    return {"message": "Healthy"}
