"""
Document loader using unstructured library.
Handles PDFs and extracts both text and tables.
"""

import os
from typing import List, Dict
from pathlib import Path
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Table, Element
from src.config.settings import settings


class DocumentLoader:
    """Load and parse PDF documents."""
    
    def __init__(self):
        """Initialize document loader."""
        pass
    
    def load_pdf(self, file_path: str) -> List[Dict]:
        """
        Load and parse a PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of dictionaries containing elements and metadata
        """
        print(f"Loading PDF: {file_path}")
        
        try:
            # Partition PDF with unstructured
            elements = partition_pdf(
                filename=file_path,
                strategy="fast",  # Use fast strategy for memory efficiency
                infer_table_structure=True,
                extract_images_in_pdf=False  # Skip images to save memory
            )
            
            # Process elements
            processed_elements = []
            for element in elements:
                element_dict = {
                    'text': str(element),
                    'type': element.category,
                    'metadata': element.metadata.to_dict() if hasattr(element, 'metadata') else {}
                }
                
                # Convert tables to markdown
                if isinstance(element, Table):
                    element_dict['is_table'] = True
                    element_dict['text'] = self._table_to_markdown(element)
                else:
                    element_dict['is_table'] = False
                
                processed_elements.append(element_dict)
            
            print(f"✓ Loaded {len(processed_elements)} elements from PDF")
            return processed_elements
            
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return []
    
    def _table_to_markdown(self, table_element: Table) -> str:
        """
        Convert table element to markdown format.
        
        Args:
            table_element: Table element from unstructured
            
        Returns:
            Markdown formatted table string
        """
        # Get table HTML and convert to markdown (simplified)
        table_text = str(table_element)
        
        # Basic markdown formatting
        # In production, use a proper HTML to markdown converter
        markdown = f"\n\n**Table:**\n{table_text}\n\n"
        
        return markdown
    
    def load_directory(self, directory_path: str) -> Dict[str, List[Dict]]:
        """
        Load all PDFs from a directory.
        
        Args:
            directory_path: Path to directory containing PDFs
            
        Returns:
            Dictionary mapping filenames to their elements
        """
        directory = Path(directory_path)
        pdf_files = list(directory.glob("*.pdf"))
        
        print(f"Found {len(pdf_files)} PDF files in {directory_path}")
        
        all_documents = {}
        for pdf_file in pdf_files:
            elements = self.load_pdf(str(pdf_file))
            all_documents[pdf_file.name] = elements
        
        return all_documents


def load_documents(source_path: str) -> Dict[str, List[Dict]]:
    """
    Load documents from a file or directory.
    
    Args:
        source_path: Path to PDF file or directory
        
    Returns:
        Dictionary mapping filenames to their elements
    """
    loader = DocumentLoader()
    
    path = Path(source_path)
    if path.is_file():
        return {path.name: loader.load_pdf(str(path))}
    elif path.is_dir():
        return loader.load_directory(str(path))
    else:
        raise ValueError(f"Invalid path: {source_path}")
