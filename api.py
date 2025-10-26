"""
FastAPI wrapper for the Financial Compliance Agentic RAG system.
Provides endpoints for query, ingestion, and health monitoring.
"""

import os
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn

from src.config.settings import settings
from src.graph.workflow import run_query
from src.vectorstore.chroma_manager import get_chroma_manager, reset_chroma_manager
from ingest import ingest_documents


# ---------------------------------------------------
# Initialize FastAPI App
# ---------------------------------------------------
app = FastAPI(
    title="Financial Compliance RAG API",
    description="Production-grade AI Retrieval-Augmented Generation system with LangGraph and Ollama.",
    version="1.0.0",
)

# Allow connections from any front-end (React, Vue, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can later replace * with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ---------------------------------------------------
# Pydantic Models
# ---------------------------------------------------
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10
    temperature: Optional[float] = settings.TEMPERATURE


class QueryResponse(BaseModel):
    query: str
    response: str
    citations: List[Dict]
    query_type: str
    documents_retrieved: int
    iterations: int


class IngestResponse(BaseModel):
    status: str
    message: str
    documents_processed: int


class HealthResponse(BaseModel):
    status: str
    collection_name: str
    document_count: int
    ollama_model: str
    embedding_model: str


# ---------------------------------------------------
# API Endpoints
# ---------------------------------------------------

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "project": "Financial Compliance Agentic RAG",
        "version": "1.0.0",
        "developer": "AI Expert System",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """System health and readiness check."""
    try:
        chroma_manager = get_chroma_manager()
        doc_count = chroma_manager.get_count()
        return HealthResponse(
            status="healthy",
            collection_name=settings.COLLECTION_NAME,
            document_count=doc_count,
            ollama_model=settings.OLLAMA_MODEL,
            embedding_model=settings.EMBEDDING_MODEL,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System unhealthy: {str(e)}")


@app.post("/api/query", response_model=QueryResponse, tags=["RAG Query"])
async def query_rag(request: QueryRequest):
    """Run a user query through the LangGraph agentic RAG system."""
    try:
        result = run_query(request.query)
        return QueryResponse(
            query=result["query"],
            response=result["response"],
            citations=result["citations"],
            query_type=result["query_type"],
            documents_retrieved=result["documents_retrieved"],
            iterations=result["iterations"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/api/ingest", tags=["Ingestion"])
async def upload_and_ingest(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    multimodal: bool = False,
    reset_collection: bool = False,
):
    """
    Upload and asynchronously ingest large PDFs.
    Returns instantly while processing continues in the background.
    """
    try:
        # Validate PDF
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        upload_dir = settings.RAW_DATA_DIR
        Path(upload_dir).mkdir(parents=True, exist_ok=True)

        # Save uploaded file
        save_path = upload_dir / file.filename
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Schedule background ingestion task
        background_tasks.add_task(
            ingest_documents,
            str(save_path),
            reset=reset_collection,
            multimodal=multimodal,
        )

        return {
            "status": "processing",
            "filename": file.filename,
            "message": "Document upload successful. Ingestion running in background.",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.get("/api/stats", tags=["System"])
async def collection_stats():
    """Get collection stats, including total document count."""
    try:
        chroma_manager = get_chroma_manager()
        return {
            "collection_name": settings.COLLECTION_NAME,
            "total_documents": chroma_manager.get_count(),
            "top_k_retrieval": settings.TOP_K_RETRIEVAL,
            "vector_dim": settings.EMBEDDING_DIMENSION,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats refresh failed: {str(e)}")


@app.delete("/api/reset", tags=["System"])
async def reset_database():
    """Clear and rebuild vector database."""
    try:
        reset_chroma_manager()
        chroma_manager = get_chroma_manager()
        chroma_manager.delete_collection()
        return {"message": "Vector database reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


# ---------------------------------------------------
# Run Server
# ---------------------------------------------------
if __name__ == "__main__":
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"\n🚀 API is live at: http://{local_ip}:8000 or http://127.0.0.1:8000\n")

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
