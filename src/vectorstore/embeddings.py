
# File 4: src/vectorstore/embeddings.py

"""
Embedding generation using sentence-transformers.
Memory-optimized for 8GB RAM systems.
"""

from typing import List
from sentence_transformers import SentenceTransformer
from src.config.settings import settings


class EmbeddingModel:
    """Wrapper for sentence-transformers embedding model."""
    
    def __init__(self):
        """Initialize the embedding model."""
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        print(f"Embedding dimension: {settings.EMBEDDING_DIMENSION}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Process in batches to manage memory
        batch_size = 32
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.model.encode(
                batch,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            all_embeddings.extend(embeddings.tolist())
        
        return all_embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        embedding = self.model.encode(
            text,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embedding.tolist()
    
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        return self.model.get_sentence_embedding_dimension()


# Global embedding model instance (singleton pattern for memory efficiency)
_embedding_model = None

def get_embedding_model() -> EmbeddingModel:
    """Get or create the global embedding model instance."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model
