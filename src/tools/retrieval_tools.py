"""
Retrieval tools for semantic search and reranking.
"""

from typing import List, Dict
from src.vectorstore.chroma_manager import ChromaManager
from src.config.settings import settings


def retrieve_documents(
    query: str,
    chroma_manager: ChromaManager,
    top_k: int = None,
    filter_dict: Dict = None
) -> List[Dict]:
    """
    Retrieve documents using semantic search.
    
    Args:
        query: Search query
        chroma_manager: ChromaDB manager instance
        top_k: Number of documents to retrieve
        filter_dict: Optional metadata filter
        
    Returns:
        List of retrieved documents
    """
    if top_k is None:
        top_k = settings.TOP_K_RETRIEVAL
    
    print(f"Retrieving top {top_k} documents for query: '{query[:50]}...'")
    
    results = chroma_manager.similarity_search(
        query=query,
        n_results=top_k,
        filter_dict=filter_dict
    )
    
    print(f"✓ Retrieved {len(results)} documents")
    
    return results


def rerank_documents(
    query: str,
    documents: List[Dict],
    top_k: int = None
) -> List[Dict]:
    """
    Rerank documents using a simple relevance scoring.
    In production, use a cross-encoder model for better reranking.
    
    Args:
        query: Search query
        documents: List of retrieved documents
        top_k: Number of documents to return after reranking
        
    Returns:
        Reranked list of documents
    """
    if top_k is None:
        top_k = settings.TOP_K_FINAL
    
    print(f"Reranking {len(documents)} documents...")
    
    # Simple reranking based on distance (lower is better)
    # Already sorted by ChromaDB, but we'll ensure it
    sorted_docs = sorted(documents, key=lambda x: x.get('distance', 999))
    
    # Return top-k
    reranked = sorted_docs[:top_k]
    
    print(f"✓ Reranked to top {len(reranked)} documents")
    
    return reranked


def hybrid_search(
    query: str,
    chroma_manager: ChromaManager,
    keywords: List[str] = None,
    top_k: int = None
) -> List[Dict]:
    """
    Perform hybrid search combining semantic and keyword search.
    
    Args:
        query: Semantic search query
        chroma_manager: ChromaDB manager instance
        keywords: Optional list of keywords for filtering
        top_k: Number of documents to retrieve
        
    Returns:
        List of retrieved documents
    """
    # For now, just semantic search
    # Can be extended to combine with keyword matching
    return retrieve_documents(query, chroma_manager, top_k)
