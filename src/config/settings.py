"""
Configuration settings for the Financial Compliance RAG system.
Loads environment variables and provides centralized config access.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "phi3:mini")
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIRECTORY: str = os.getenv(
        "CHROMA_PERSIST_DIRECTORY", 
        str(DATA_DIR / "chroma_db")
    )
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "financial_compliance")
    
    # Chunking Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # Retrieval Configuration
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "10"))
    TOP_K_FINAL: int = int(os.getenv("TOP_K_FINAL", "3"))
    
    # Agent Configuration
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "3"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    
    # Multi-Modal Configuration (NEW)
    MAX_IMAGE_PAGES: int = int(os.getenv("MAX_IMAGE_PAGES", "50"))
    MIN_IMAGE_SIZE: int = int(os.getenv("MIN_IMAGE_SIZE", "10000"))
    ENABLE_IMAGE_FILTERING: bool = os.getenv("ENABLE_IMAGE_FILTERING", "true").lower() == "true"
    
    # Document types for metadata
    DOCUMENT_TYPES: list = [
        "regulation",
        "policy",
        "guideline",
        "compliance_report",
        "audit_document"
    ]
    
    # Compliance categories
    COMPLIANCE_CATEGORIES: list = [
        "AML",  # Anti-Money Laundering
        "KYC",  # Know Your Customer
        "Basel_III",
        "GDPR",
        "SOX",  # Sarbanes-Oxley
        "FCRA",  # Fair Credit Reporting Act
        "TILA",  # Truth in Lending Act
        "RESPA"  # Real Estate Settlement Procedures Act
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.DATA_DIR.mkdir(exist_ok=True)
        self.RAW_DATA_DIR.mkdir(exist_ok=True)
        self.PROCESSED_DATA_DIR.mkdir(exist_ok=True)
        Path(self.CHROMA_PERSIST_DIRECTORY).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()
