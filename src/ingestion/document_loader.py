"""
Document loader using PyPDF2 for better Windows compatibility.
"""

import os
from typing import List, Dict
from pathlib import Path
import PyPDF2
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
            processed_elements = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():  # Only add if text exists
                        element_dict = {
                            'text': text,
                            'type': 'paragraph',
                            'metadata': {
                                'page_number': page_num + 1,
                                'filename': os.path.basename(file_path)
                            },
                            'is_table': False
                        }
                        processed_elements.append(element_dict)
            
            print(f"✓ Loaded {len(processed_elements)} pages from PDF")
            return processed_elements
            
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return []
    
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
