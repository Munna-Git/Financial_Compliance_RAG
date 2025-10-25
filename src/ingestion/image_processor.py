"""
Optimized image processing for multi-modal RAG.
Only processes pages that actually contain images/charts.
"""

import os
from typing import List, Dict, Optional, Set
from pathlib import Path
from PIL import Image
import io
import PyPDF2
from pdf2image import convert_from_path
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

from src.config.settings import settings


class ImageProcessor:
    """Optimized image processor that only processes pages with actual images."""
    
    def __init__(self):
        """Initialize image processor with BLIP model."""
        print("Loading BLIP image captioning model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Use BLIP for image captioning (lightweight, good for 8GB RAM)
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        ).to(self.device)
        
        print(f"BLIP model loaded on {self.device}")
    
    def detect_image_pages(self, pdf_path: str) -> Set[int]:
        """
        Detect which pages contain actual images (not just text).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Set of page numbers (0-indexed) that contain images
        """
        image_pages = set()
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    # Check if page has XObject (images/forms)
                    if '/XObject' in page.get('/Resources', {}):
                        xobject = page['/Resources']['/XObject'].get_object()
                        
                        # Check each XObject
                        for obj_name in xobject:
                            obj = xobject[obj_name]
                            
                            # Check if it's an image (has /Subtype /Image)
                            if obj.get('/Subtype') == '/Image':
                                # Optional: Check image size to filter out small logos/icons
                                if settings.ENABLE_IMAGE_FILTERING:
                                    try:
                                        width = obj.get('/Width', 0)
                                        height = obj.get('/Height', 0)
                                        
                                        # Only include images above minimum size
                                        if width * height > settings.MIN_IMAGE_SIZE:
                                            image_pages.add(page_num)
                                            break
                                    except:
                                        # If we can't get size, include it
                                        image_pages.add(page_num)
                                        break
                                else:
                                    image_pages.add(page_num)
                                    break
            
            print(f"  Detected {len(image_pages)} pages with images out of {len(pdf_reader.pages)} total pages")
            
        except Exception as e:
            print(f"  Warning: Could not detect image pages: {e}")
            print(f"  Falling back to processing first {settings.MAX_IMAGE_PAGES} pages")
            # Fallback: return first MAX_IMAGE_PAGES
            return set(range(min(settings.MAX_IMAGE_PAGES, 100)))
        
        return image_pages
    
    def extract_images_from_pdf(self, pdf_path: str, output_dir: str = None) -> List[Dict]:
        """
        Extract and caption only pages that contain images.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save extracted images (optional)
            
        Returns:
            List of dictionaries with image info and captions
        """
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"Analyzing PDF for images: {pdf_path}...")
        
        # Step 1: Detect which pages have images
        image_pages = self.detect_image_pages(pdf_path)
        
        if not image_pages:
            print("  No significant images found in PDF")
            return []
        
        # Step 2: Limit to MAX_IMAGE_PAGES
        image_pages = sorted(list(image_pages))[:settings.MAX_IMAGE_PAGES]
        
        print(f"  Processing {len(image_pages)} pages with images...")
        
        images_info = []
        
        try:
            # Step 3: Convert only pages with images
            # We need to convert in batches because pdf2image doesn't support discontinuous pages
            for page_num in image_pages:
                # Convert single page (page_num is 0-indexed, pdf2image uses 1-indexed)
                page_images = convert_from_path(
                    pdf_path, 
                    dpi=150,
                    first_page=page_num + 1,
                    last_page=page_num + 1
                )
                
                if page_images:
                    page_image = page_images[0]
                    
                    # Generate caption
                    caption = self.generate_caption(page_image)
                    
                    image_info = {
                        'page_number': page_num + 1,  # 1-indexed for display
                        'caption': caption,
                        'type': 'page_image',
                        'source_pdf': os.path.basename(pdf_path)
                    }
                    
                    # Save image if output directory provided
                    if output_dir:
                        image_path = os.path.join(
                            output_dir, 
                            f"{Path(pdf_path).stem}_page_{page_num + 1}.png"
                        )
                        page_image.save(image_path)
                        image_info['image_path'] = image_path
                    
                    images_info.append(image_info)
                    print(f"  Page {page_num + 1}: {caption[:60]}...")
            
            print(f"✓ Processed {len(images_info)} image pages")
            
        except Exception as e:
            print(f"Error processing images: {e}")
        
        return images_info
    
    def generate_caption(self, image: Image.Image) -> str:
        """
        Generate caption for an image using BLIP.
        
        Args:
            image: PIL Image object
            
        Returns:
            Generated caption string
        """
        try:
            # Resize large images to save memory
            max_size = (512, 512)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Process image
            inputs = self.processor(image, return_tensors="pt").to(self.device)
            
            # Generate caption
            with torch.no_grad():
                out = self.model.generate(**inputs, max_length=50)
            
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            return caption
            
        except Exception as e:
            print(f"Error generating caption: {e}")
            return "Image content could not be processed"


# Singleton instance
_image_processor = None

def get_image_processor() -> ImageProcessor:
    """Get or create global image processor instance."""
    global _image_processor
    if _image_processor is None:
        _image_processor = ImageProcessor()
    return _image_processor
