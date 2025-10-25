"""
Document loader with optimized multi-modal support.
Handles PDFs with text, images, charts, and diagrams efficiently.
"""

import os
from typing import List, Dict
from pathlib import Path
import PyPDF2
from src.config.settings import settings


class DocumentLoader:
    """Load and parse PDF documents with optimized multi-modal support."""
    
    def __init__(self, enable_multimodal: bool = False):
        """
        Initialize document loader.
        
        Args:
            enable_multimodal: Whether to enable image extraction and captioning
        """
        self.enable_multimodal = enable_multimodal
        
        if enable_multimodal:
            from src.ingestion.image_processor import get_image_processor
            self.image_processor = get_image_processor()
    
    def load_pdf(self, file_path: str) -> List[Dict]:
        """
        Load and parse a PDF file with optional optimized multi-modal processing.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of dictionaries containing elements and metadata
        """
        print(f"\nLoading PDF: {file_path}")
        
        processed_elements = []
        
        try:
            # Extract text content
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                print(f"  Total pages: {num_pages}")
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        element_dict = {
                            'text': text,
                            'type': 'text',
                            'metadata': {
                                'page_number': page_num + 1,
                                'filename': os.path.basename(file_path)
                            },
                            'is_table': False
                        }
                        processed_elements.append(element_dict)
            
            print(f"  ✓ Extracted text from {len(processed_elements)} pages")
            
            # Extract and caption images if multi-modal enabled
            if self.enable_multimodal:
                print(f"  Scanning for images/charts...")
                images_info = self.image_processor.extract_images_from_pdf(
                    file_path,
                    output_dir=str(settings.PROCESSED_DATA_DIR / "images")
                )
                
                # Add image descriptions as searchable elements
                for img_info in images_info:
                    image_element = {
                        'text': f"[IMAGE/CHART on page {img_info['page_number']}] {img_info['caption']}",
                        'type': 'image',
                        'metadata': {
                            'page_number': img_info['page_number'],
                            'filename': os.path.basename(file_path),
                            'image_path': img_info.get('image_path', ''),
                            'is_chart': True
                        },
                        'is_table': False
                    }
                    processed_elements.append(image_element)
                
                if images_info:
                    print(f"  ✓ Added {len(images_info)} image descriptions")
                else:
                    print(f"  ℹ No significant images/charts detected")
            
            return processed_elements
            
        except Exception as e:
            print(f"  ✗ Error loading PDF: {e}")
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
        
        print(f"\n{'='*60}")
        print(f"Found {len(pdf_files)} PDF files in {directory_path}")
        print(f"{'='*60}")
        
        all_documents = {}
        for idx, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{idx}/{len(pdf_files)}] Processing: {pdf_file.name}")
            elements = self.load_pdf(str(pdf_file))
            all_documents[pdf_file.name] = elements
        
        return all_documents


def load_documents(source_path: str, enable_multimodal: bool = False) -> Dict[str, List[Dict]]:
    """
    Load documents from a file or directory.
    
    Args:
        source_path: Path to PDF file or directory
        enable_multimodal: Whether to enable optimized image processing
        
    Returns:
        Dictionary mapping filenames to their elements
    """
    loader = DocumentLoader(enable_multimodal=enable_multimodal)
    
    path = Path(source_path)
    if path.is_file():
        return {path.name: loader.load_pdf(str(path))}
    elif path.is_dir():
        return loader.load_directory(str(path))
    else:
        raise ValueError(f"Invalid path: {source_path}")
