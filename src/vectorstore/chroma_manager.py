"""
ChromaDB manager for vector storage and retrieval.
Optimized for memory efficiency on 8GB RAM systems.
"""

from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from src.config.settings import settings
from src.vectorstore.embeddings import get_embedding_model


class ChromaManager:
    """Manages ChromaDB operations for document storage and retrieval."""
    
    def __init__(self):
        """Initialize ChromaDB client and collection."""
        print(f"Initializing ChromaDB at: {settings.CHROMA_PERSIST_DIRECTORY}")
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get embedding model
        self.embedding_model = get_embedding_model()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"description": "Financial compliance documents"}
        )
        
        print(f"Collection '{settings.COLLECTION_NAME}' ready")
        print(f"Current document count: {self.collection.count()}")
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict],
        ids: List[str]
    ) -> None:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text chunks
            metadatas: List of metadata dictionaries
            ids: List of unique IDs for each chunk
        """
        if not texts:
            print("No documents to add")
            return
        
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedding_model.embed_documents(texts)
        
        print(f"Adding {len(texts)} documents to ChromaDB...")
        
        # Add in batches to manage memory
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            end_idx = min(i + batch_size, len(texts))
            
            self.collection.add(
                documents=texts[i:end_idx],
                embeddings=embeddings[i:end_idx],
                metadatas=metadatas[i:end_idx],
                ids=ids[i:end_idx]
            )
        
        print(f"✓ Successfully added {len(texts)} documents")
        print(f"Total documents in collection: {self.collection.count()}")
    
    def similarity_search(
        self,
        query: str,
        n_results: int = None,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar documents using semantic similarity.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of result dictionaries with text, metadata, and distance
        """
        if n_results is None:
            n_results = settings.TOP_K_RETRIEVAL
        
        # Generate query embedding
        query_embedding = self.embedding_model.embed_query(query)
        
        # Perform search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'id': results['ids'][0][i]
            })
        
        return formatted_results
    
    def delete_collection(self) -> None:
        """Delete the entire collection."""
        self.client.delete_collection(settings.COLLECTION_NAME)
        print(f"Collection '{settings.COLLECTION_NAME}' deleted")
    
    def get_count(self) -> int:
        """Get the number of documents in the collection."""
        return self.collection.count()


# Global ChromaDB manager instance
_chroma_manager = None

def get_chroma_manager() -> ChromaManager:
    """Get or create the global ChromaDB manager instance."""
    global _chroma_manager
    if _chroma_manager is None:
        _chroma_manager = ChromaManager()
    return _chroma_manager
