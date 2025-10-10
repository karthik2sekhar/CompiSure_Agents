"""
LandingAI ADE Extraction Service
Advanced document extraction using LandingAI's DPT-2 model for commission statements
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import pandas as pd
import re

try:
    from landingai_ade import LandingAIADE
    LANDINGAI_AVAILABLE = True
except ImportError:
    LANDINGAI_AVAILABLE = False

class LandingAIExtractionService:
    """Service for extracting commission data using LandingAI ADE SDK"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = None
        self._initialize_client()
        
        # Carrier-specific field mappings
        self.carrier_mappings = {
            'humana': {
                'statement_date_patterns': ['Statement date', 'for period ending'],
                'policy_patterns': ['N\\d{11}A', 'M\\d{11}A', '\\d{11}A'],
                'amount_patterns': ['Paid amount', 'Total commissions'],
                'member_patterns': ['Norris William', 'Neill Kathleen', 'O\'Neill Kathleen'],
                'table_identifiers': ['Product type', 'Month paid', 'Paid amount']
            },
            'hc': {
                'statement_date_patterns': ['Statement Date', 'Period Ending'],
                'policy_patterns': ['\\d{6}_[A-Z]'],
                'amount_patterns': ['Commission Amount', 'Total Amount'],
                'member_patterns': ['Member Name', 'Employee Name'],
                'table_identifiers': ['Policy', 'Member', 'Amount']
            },
            'hne': {
                'statement_date_patterns': ['Statement Date', 'Period'],
                'policy_patterns': ['\\d{11}'],
                'amount_patterns': ['Commission', 'Amount'],
                'member_patterns': ['Member'],
                'table_identifiers': ['Policy Number', 'Commission Amount']
            }
        }
    
    def _initialize_client(self):
        """Initialize the LandingAI ADE client"""
        if not LANDINGAI_AVAILABLE:
            self.logger.error("LandingAI ADE SDK not available. Install with: pip install landingai-ade")
            return
            
        api_key = os.environ.get("VISION_AGENT_API_KEY")
        if not api_key or api_key == 'your_landingai_api_key_here':
            self.logger.warning("VISION_AGENT_API_KEY not configured. LandingAI extraction disabled.")
            return
            
        try:
            self.client = LandingAIADE(apikey=api_key)
            self.logger.info("LandingAI ADE client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize LandingAI client: {str(e)}")
    
    def extract_commission_data(self, pdf_path: str, carrier: str = None) -> Dict[str, Any]:
        """
        Extract commission data from PDF using LandingAI ADE
        
        Args:
            pdf_path: Path to the PDF file
            carrier: Carrier identifier (humana, hc, hne, etc.)
            
        Returns:
            Dictionary containing extracted commission data
        """
        if not self.client:
            self.logger.error("LandingAI client not initialized")
            return {"error": "LandingAI client not available"}
            
        try:
            self.logger.info(f"Starting LandingAI extraction for: {pdf_path}")
            
            # Parse document with DPT-2 model
            parse_response = self.client.parse(
                document=Path(pdf_path),
                model="dpt-2-latest"
            )
            
            self.logger.info("LandingAI parsing completed successfully")
            
            # Extract and normalize data
            extracted_data = self._normalize_extraction_data(parse_response, carrier)
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"LandingAI extraction failed: {str(e)}")
            return {"error": f"Extraction failed: {str(e)}"}
    
    def _normalize_extraction_data(self, parse_response: Any, carrier: str = None) -> Dict[str, Any]:
        """
        Normalize the LandingAI response into structured commission data
        
        Args:
            parse_response: Raw response from LandingAI
            carrier: Carrier identifier for specific processing
            
        Returns:
            Normalized commission data dictionary
        """
        try:
            # Convert response to dictionary if needed
            if hasattr(parse_response, 'dict'):
                data = parse_response.dict()
            elif hasattr(parse_response, 'model_dump'):
                data = parse_response.model_dump()
            else:
                data = parse_response
            
            # Extract key information
            result = {
                'carrier': carrier or self._detect_carrier(data),
                'statement_date': self._extract_statement_date(data, carrier),
                'agent_info': self._extract_agent_info(data),
                'commission_entries': self._extract_commission_entries(data, carrier),
                'total_amount': self._extract_total_amount(data, carrier),
                'metadata': {
                    'pages': data.get('metadata', {}).get('page_count', 0),
                    'extraction_method': 'landingai_ade',
                    'model': 'dpt-2-latest'
                }
            }
            
            # Log extraction summary
            entry_count = len(result.get('commission_entries', []))
            self.logger.info(f"LandingAI extraction completed: {entry_count} entries, total: ${result.get('total_amount', 0)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Data normalization failed: {str(e)}")
            return {"error": f"Normalization failed: {str(e)}"}
    
    def _detect_carrier(self, data: Dict) -> str:
        """Detect carrier from document content"""
        content = str(data.get('markdown', '')).lower()
        
        if 'humana' in content:
            return 'humana'
        elif 'health connector' in content or 'hc' in content:
            return 'hc'
        elif 'health new england' in content or 'hne' in content:
            return 'hne'
        elif 'blue cross' in content:
            return 'blue_cross'
        elif 'aetna' in content:
            return 'aetna'
        elif 'cigna' in content:
            return 'cigna'
        elif 'unitedhealth' in content:
            return 'unitedhealth'
        
        return 'unknown'
    
    def _extract_statement_date(self, data: Dict, carrier: str = None) -> Optional[str]:
        """Extract statement date from document"""
        content = data.get('markdown', '')
        
        # Common date patterns
        date_patterns = [
            r'Statement date\s*([A-Z][a-z]+ \d{1,2}, \d{4})',
            r'for period ending ([A-Z][a-z]+ \d{1,2}, \d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{2})',
            r'([A-Z][a-z]+ \d{1,2}, \d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    # Try to parse and standardize the date
                    if '/' in date_str:
                        if len(date_str.split('/')[-1]) == 2:
                            # Convert 2-digit year to 4-digit
                            parts = date_str.split('/')
                            year = int(parts[2])
                            if year < 50:
                                year += 2000
                            else:
                                year += 1900
                            date_str = f"{parts[0]}/{parts[1]}/{year}"
                        
                        parsed_date = datetime.strptime(date_str, '%m/%d/%Y')
                    else:
                        parsed_date = datetime.strptime(date_str, '%B %d, %Y')
                    
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        self.logger.warning("Could not extract statement date from document")
        return None
    
    def _extract_agent_info(self, data: Dict) -> Dict[str, str]:
        """Extract agent information from document"""
        content = data.get('markdown', '')
        agent_info = {}
        
        # Extract agent name
        agent_patterns = [
            r'Agent\s*([A-Z][A-Z\s]+)',
            r'EVANS ([A-Z\s]+)',
            r'Agent number\s*(\d+)'
        ]
        
        for pattern in agent_patterns:
            match = re.search(pattern, content)
            if match:
                if 'number' in pattern.lower():
                    agent_info['agent_number'] = match.group(1)
                else:
                    agent_info['agent_name'] = match.group(1).strip()
        
        return agent_info
    
    def _extract_commission_entries(self, data: Dict, carrier: str = None) -> List[Dict[str, Any]]:
        """Extract individual commission entries from tables"""
        entries = []
        
        try:
            # Look for table data in chunks
            chunks = data.get('chunks', [])
            
            for chunk in chunks:
                if chunk.get('type') == 'table':
                    table_entries = self._parse_table_chunk(chunk, carrier)
                    entries.extend(table_entries)
            
            # If no table chunks, try to extract from markdown tables
            if not entries:
                entries = self._extract_from_markdown_tables(data.get('markdown', ''), carrier)
            
        except Exception as e:
            self.logger.error(f"Failed to extract commission entries: {str(e)}")
        
        return entries
    
    def _parse_table_chunk(self, chunk: Dict, carrier: str = None) -> List[Dict[str, Any]]:
        """Parse a table chunk to extract commission entries"""
        entries = []
        markdown = chunk.get('markdown', '')
        
        # Extract table using regex
        table_pattern = r'<table[^>]*>(.*?)</table>'
        table_match = re.search(table_pattern, markdown, re.DOTALL)
        
        if table_match:
            table_html = table_match.group(1)
            
            # Extract rows
            row_pattern = r'<tr[^>]*>(.*?)</tr>'
            rows = re.findall(row_pattern, table_html, re.DOTALL)
            
            headers = []
            for i, row in enumerate(rows):
                # Extract cells
                cell_pattern = r'<t[hd][^>]*[^>]*>(.*?)</t[hd]>'
                cells = re.findall(cell_pattern, row, re.DOTALL)
                cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                
                if i == 0:  # Header row
                    headers = cells
                elif cells and len(cells) >= 3:  # Data row
                    entry = self._create_entry_from_cells(headers, cells, carrier)
                    if entry:
                        entries.append(entry)
        
        return entries
    
    def _extract_from_markdown_tables(self, markdown: str, carrier: str = None) -> List[Dict[str, Any]]:
        """Extract commission entries from markdown table format"""
        entries = []
        
        # Look for member/policy patterns in text
        if carrier == 'humana':
            # Humana-specific extraction
            member_pattern = r'([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z])?)\s+([NM]\d{11}A).*?\$(\d+\.?\d*)'
            matches = re.findall(member_pattern, markdown)
            
            for match in matches:
                entries.append({
                    'member_name': match[0],
                    'policy_id': match[1],
                    'commission_amount': float(match[2]),
                    'carrier': 'humana'
                })
        
        return entries
    
    def _create_entry_from_cells(self, headers: List[str], cells: List[str], carrier: str = None) -> Optional[Dict[str, Any]]:
        """Create a commission entry from table cells"""
        if not headers or not cells:
            return None
        
        entry = {'carrier': carrier}
        
        # Map cells to standardized fields
        for i, header in enumerate(headers):
            if i < len(cells):
                value = cells[i].strip()
                
                # Map header to standard field
                header_lower = header.lower()
                if 'amount' in header_lower or 'paid' in header_lower:
                    try:
                        # Extract numeric value
                        amount_match = re.search(r'\$?(\d+\.?\d*)', value)
                        if amount_match:
                            entry['commission_amount'] = float(amount_match.group(1))
                    except ValueError:
                        pass
                elif 'policy' in header_lower or 'member' in header_lower:
                    entry['policy_id'] = value
                elif 'name' in header_lower:
                    entry['member_name'] = value
                elif 'date' in header_lower or 'month' in header_lower:
                    entry['service_period'] = value
        
        # Only return entry if it has essential data
        if entry.get('commission_amount') is not None:
            return entry
        
        return None
    
    def _extract_total_amount(self, data: Dict, carrier: str = None) -> float:
        """Extract total commission amount from document"""
        content = data.get('markdown', '')
        
        # Look for total patterns
        total_patterns = [
            r'Total commissions[^$]*\$(\d+\.?\d*)',
            r'Amount due to you[^$]*\$(\d+\.?\d*)',
            r'Total[^$]*\$(\d+\.?\d*)',
            r'Agent total[^$]*\$(\d+\.?\d*)'
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return 0.0
    
    def to_dataframe(self, extraction_result: Dict[str, Any]) -> pd.DataFrame:
        """Convert extraction result to pandas DataFrame"""
        entries = extraction_result.get('commission_entries', [])
        
        if not entries:
            return pd.DataFrame()
        
        # Add common fields to each entry
        for entry in entries:
            entry['statement_date'] = extraction_result.get('statement_date')
            entry['extraction_method'] = 'landingai_ade'
        
        return pd.DataFrame(entries)
    
    def is_available(self) -> bool:
        """Check if LandingAI extraction is available"""
        return LANDINGAI_AVAILABLE and self.client is not None