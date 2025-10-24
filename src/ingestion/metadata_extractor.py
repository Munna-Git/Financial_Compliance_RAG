"""
Extract hierarchical metadata from documents.
"""

from typing import Dict, List
import re
from datetime import datetime
from src.config.settings import settings


class MetadataExtractor:
    """Extract and enrich metadata for document chunks."""
    
    def __init__(self):
        """Initialize metadata extractor."""
        self.compliance_keywords = {
            'AML': ['anti-money laundering', 'aml', 'suspicious activity', 'customer due diligence'],
            'KYC': ['know your customer', 'kyc', 'customer identification', 'identity verification'],
            'Basel_III': ['basel', 'capital adequacy', 'leverage ratio', 'liquidity coverage'],
            'GDPR': ['gdpr', 'data protection', 'privacy', 'personal data'],
            'SOX': ['sarbanes-oxley', 'sox', 'internal controls', 'financial reporting'],
            'FCRA': ['fair credit reporting', 'fcra', 'credit report', 'consumer reporting'],
            'TILA': ['truth in lending', 'tila', 'apr', 'finance charge'],
            'RESPA': ['respa', 'real estate settlement', 'closing disclosure', 'loan estimate']
        }
    
    def extract_metadata(
    self,
    text: str,
    element_metadata: Dict,
    filename: str,
    chunk_index: int
) -> Dict:
        """
            Extract comprehensive metadata from text and context.
            
            Args:
                text: Text content
                element_metadata: Original element metadata from unstructured
                filename: Source filename
                chunk_index: Index of chunk in document
                
            Returns:
                Dictionary of metadata
            """
        metadata = {
            'filename': filename,
            'chunk_index': chunk_index,
            'chunk_length': len(text),
            'timestamp': datetime.now().isoformat(),
        }
        
        # Extract document type
        metadata['doc_type'] = self._identify_document_type(filename, text)
        
        # Extract compliance categories - CONVERT LIST TO STRING
        categories = self._identify_compliance_categories(text)
        metadata['compliance_categories'] = ','.join(categories) if categories else 'general'
        
        # Extract section information
        metadata['section'] = self._extract_section(text, element_metadata)
        
        # Add page number if available
        if 'page_number' in element_metadata:
            metadata['page_number'] = element_metadata['page_number']
        
        # Extract dates mentioned in text - CONVERT LIST TO STRING
        dates = self._extract_dates(text)
        if dates:
            metadata['mentioned_dates'] = ','.join(dates)
        
        return metadata

    
    def _identify_document_type(self, filename: str, text: str) -> str:
        """Identify document type from filename and content."""
        filename_lower = filename.lower()
        text_lower = text.lower()
        
        if 'regulation' in filename_lower or 'cfr' in text_lower:
            return 'regulation'
        elif 'policy' in filename_lower or 'policy' in text_lower:
            return 'policy'
        elif 'guideline' in filename_lower or 'guidance' in text_lower:
            return 'guideline'
        elif 'audit' in filename_lower or 'audit' in text_lower:
            return 'audit_document'
        elif 'compliance' in filename_lower or 'compliance report' in text_lower:
            return 'compliance_report'
        else:
            return 'general'
    
    def _identify_compliance_categories(self, text: str) -> List[str]:
        """Identify relevant compliance categories from text."""
        text_lower = text.lower()
        categories = []
        
        for category, keywords in self.compliance_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    categories.append(category)
                    break
        
        return categories if categories else ['general']
    
    def _extract_section(self, text: str, element_metadata: Dict) -> str:
        """Extract section header information."""
        # Check if element type is a header
        if element_metadata.get('type') in ['Title', 'Header']:
            return text[:100]  # First 100 chars as section name
        
        # Try to find section numbers (e.g., "Section 1.2.3")
        section_pattern = r'(?:Section|Article|Chapter)\s+[\d\.]+:?\s*([^\n]+)'
        match = re.search(section_pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(0)[:100]
        
        return 'unknown'
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates mentioned in text."""
        # Simple date patterns (extend as needed)
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{4}-\d{2}-\d{2}\b',       # YYYY-MM-DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return list(set(dates))[:5]  # Return up to 5 unique dates
