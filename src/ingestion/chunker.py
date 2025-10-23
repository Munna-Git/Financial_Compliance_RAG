"""
Semantic chunking for documents.
Creates meaningful chunks based on sentence boundaries and document structure.
"""

from typing import List, Dict
from sentence_transformers import SentenceTransformer
from src.config.settings import settings
import re


class SemanticChunker:
    """Chunk documents semantically based on sentence boundaries."""
    
    def __init__(self):
        """Initialize semantic chunker."""
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def chunk_elements(self, elements: List[Dict]) -> List[Dict]:
        """
        Chunk document elements into semantic chunks.
        
        Args:
            elements: List of document elements from document loader
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        
        for element in elements:
            text = element['text']
            element_type = element['type']
            is_table = element.get('is_table', False)
            
            # Keep tables as single chunks
            if is_table:
                chunks.append({
                    'text': text,
                    'element_type': element_type,
                    'is_table': True,
                    'original_metadata': element.get('metadata', {})
                })
            else:
                # Split text elements into semantic chunks
                text_chunks = self._chunk_text(text)
                
                for chunk_text in text_chunks:
                    chunks.append({
                        'text': chunk_text,
                        'element_type': element_type,
                        'is_table': False,
                        'original_metadata': element.get('metadata', {})
                    })
        
        return chunks
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks based on sentence boundaries.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        # Split into sentences
        sentences = self._split_sentences(text)
        
        if not sentences:
            return []
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence would exceed chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(' '.join(current_chunk))
                
                # Start new chunk with overlap
                # Keep last few sentences for overlap
                overlap_sentences = []
                overlap_length = 0
                for s in reversed(current_chunk):
                    if overlap_length + len(s) <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_length += len(s)
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_length = overlap_length
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Basic sentence splitting (can be improved with nltk or spacy)
        # Split on periods, exclamations, questions followed by space and capital letter
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, text)
        
        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences


def chunk_documents(documents: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
    """
    Chunk all documents.
    
    Args:
        documents: Dictionary mapping filenames to elements
        
    Returns:
        Dictionary mapping filenames to chunks
    """
    chunker = SemanticChunker()
    
    chunked_documents = {}
    for filename, elements in documents.items():
        print(f"Chunking {filename}...")
        chunks = chunker.chunk_elements(elements)
        chunked_documents[filename] = chunks
        print(f"  Created {len(chunks)} chunks")
    
    return chunked_documents
