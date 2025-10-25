"""
Document ingestion script with optimized multi-modal support.
Processes PDFs and indexes them into ChromaDB.
"""

import sys
from pathlib import Path
from tqdm import tqdm

from src.config.settings import settings
from src.ingestion.document_loader import load_documents
from src.ingestion.chunker import chunk_documents
from src.ingestion.metadata_extractor import MetadataExtractor
from src.vectorstore.chroma_manager import get_chroma_manager, reset_chroma_manager


def ingest_documents(source_path: str, reset: bool = False, multimodal: bool = False):
    """
    Ingest documents from a file or directory.
    
    Args:
        source_path: Path to PDF file or directory
        reset: Whether to reset the collection before ingesting
        multimodal: Whether to enable optimized image/chart processing
    """
    print(f"\n{'='*60}")
    print("DOCUMENT INGESTION PIPELINE")
    if multimodal:
        print(f"Multi-Modal Mode: ENABLED")
        print(f"  Max image pages per PDF: {settings.MAX_IMAGE_PAGES}")
        print(f"  Min image size: {settings.MIN_IMAGE_SIZE} pixels")
        print(f"  Image filtering: {settings.ENABLE_IMAGE_FILTERING}")
    else:
        print(f"Multi-Modal Mode: DISABLED (text-only)")
    print(f"{'='*60}\n")
    
    # Step 1: Load documents
    print("Step 1: Loading documents...")
    documents = load_documents(source_path, enable_multimodal=multimodal)
    
    total_elements = sum(len(elements) for elements in documents.values())
    print(f"\n✓ Loaded {len(documents)} document(s) with {total_elements} total elements\n")
    
    # Step 2: Chunk documents
    print("Step 2: Chunking documents...")
    chunked_docs = chunk_documents(documents)
    
    total_chunks = sum(len(chunks) for chunks in chunked_docs.values())
    print(f"✓ Created {total_chunks} total chunks\n")
    
    # Step 3: Extract metadata
    print("Step 3: Extracting metadata...")
    metadata_extractor = MetadataExtractor()
    
    all_texts = []
    all_metadatas = []
    all_ids = []
    
    chunk_id = 0
    for filename, chunks in chunked_docs.items():
        for idx, chunk in enumerate(tqdm(chunks, desc=f"  {filename[:40]}")):
            text = chunk['text']
            
            # Extract metadata
            metadata = metadata_extractor.extract_metadata(
                text=text,
                element_metadata=chunk.get('original_metadata', {}),
                filename=filename,
                chunk_index=idx
            )
            
            # Add element type info
            metadata['element_type'] = chunk.get('element_type', 'unknown')
            metadata['is_table'] = chunk.get('is_table', False)
            
            all_texts.append(text)
            all_metadatas.append(metadata)
            all_ids.append(f"chunk_{chunk_id}")
            
            chunk_id += 1
    
    print(f"✓ Extracted metadata for {len(all_texts)} chunks\n")
    
    # Step 4: Initialize ChromaDB
    print("Step 4: Initializing vector store...")
    
    if reset:
        print("  Resetting existing collection...")
        reset_chroma_manager()
    
    chroma_manager = get_chroma_manager()
    
    if reset:
        chroma_manager.delete_collection()
    
    # Step 5: Add to vector store
    print("\nStep 5: Adding documents to vector store...")
    chroma_manager.add_documents(
        texts=all_texts,
        metadatas=all_metadatas,
        ids=all_ids
    )
    
    print(f"\n{'='*60}")
    print("INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"Total documents in collection: {chroma_manager.get_count()}")
    
    # Summary
    if multimodal:
        image_chunks = sum(1 for m in all_metadatas if m.get('element_type') == 'image')
        text_chunks = len(all_metadatas) - image_chunks
        print(f"  Text chunks: {text_chunks}")
        print(f"  Image/chart chunks: {image_chunks}")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <path_to_pdf_or_directory> [--reset] [--multimodal]")
        print("\nExamples:")
        print("  python ingest.py data/raw/")
        print("  python ingest.py data/raw/ --reset")
        print("  python ingest.py data/raw/ --multimodal")
        print("  python ingest.py data/raw/ --reset --multimodal")
        print("\nConfiguration (via .env):")
        print(f"  MAX_IMAGE_PAGES={settings.MAX_IMAGE_PAGES}")
        print(f"  MIN_IMAGE_SIZE={settings.MIN_IMAGE_SIZE}")
        print(f"  ENABLE_IMAGE_FILTERING={settings.ENABLE_IMAGE_FILTERING}")
        sys.exit(1)
    
    source_path = sys.argv[1]
    reset = "--reset" in sys.argv
    multimodal = "--multimodal" in sys.argv
    
    ingest_documents(source_path, reset=reset, multimodal=multimodal)
