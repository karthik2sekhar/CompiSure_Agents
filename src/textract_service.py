"""
Amazon Textract PDF Extraction Service
Handles PDF text and table extraction using AWS Textract
"""

import boto3
import json
import logging
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from botocore.exceptions import ClientError, NoCredentialsError
import pandas as pd
from datetime import datetime
import re
from .textract_config import TEXTRACT_CONFIG, CARRIER_FIELD_MAPPINGS, EXTRACTION_QUALITY_THRESHOLDS

class TextractExtractionService:
    """Service for extracting data from PDFs using Amazon Textract"""
    
    def __init__(self):
        """Initialize the Textract service"""
        self.logger = logging.getLogger(__name__)
        self.textract_client = None
        self._initialize_textract_client()
        
    def _initialize_textract_client(self):
        """Initialize the AWS Textract client"""
        try:
            # Initialize boto3 client
            self.textract_client = boto3.client(
                'textract',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.logger.info("Amazon Textract client initialized successfully")
        except NoCredentialsError:
            self.logger.error("AWS credentials not found. Please configure AWS credentials.")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Textract client: {str(e)}")
            raise
    
    def extract_from_pdf(self, pdf_path: str, carrier: str) -> Dict[str, Any]:
        """
        Extract commission data from PDF using Textract
        
        Args:
            pdf_path: Path to the PDF file
            carrier: Carrier name (hc, hne, humana, etc.)
            
        Returns:
            Dictionary containing extracted commission data
        """
        try:
            self.logger.info(f"Starting Textract extraction for {carrier} PDF: {pdf_path}")
            
            # Read PDF file
            with open(pdf_path, 'rb') as pdf_file:
                pdf_bytes = pdf_file.read()
            
            # Call Textract to analyze document with tables
            response = self.textract_client.analyze_document(
                Document={'Bytes': pdf_bytes},
                FeatureTypes=['TABLES', 'FORMS']
            )
            
            # Extract text, tables, and key-value pairs
            text_content = self._extract_text(response)
            tables = self._extract_tables(response)
            key_value_pairs = self._extract_key_value_pairs(response)
            
            # Process carrier-specific data
            extracted_data = self._process_carrier_data(
                carrier, text_content, tables, key_value_pairs, pdf_path
            )
            
            self.logger.info(f"Successfully extracted {len(extracted_data.get('entries', []))} entries from {carrier} PDF")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error extracting data from {pdf_path}: {str(e)}")
            raise
    
    def _extract_text(self, response: Dict) -> str:
        """Extract raw text from Textract response"""
        text_lines = []
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                text_lines.append(block.get('Text', ''))
        return '\n'.join(text_lines)
    
    def _extract_tables(self, response: Dict) -> List[List[str]]:
        """Extract table data from Textract response"""
        tables = []
        
        # Create a map of block IDs to blocks
        block_map = {block['Id']: block for block in response.get('Blocks', [])}
        
        # Find table blocks
        table_blocks = [block for block in response.get('Blocks', []) if block['BlockType'] == 'TABLE']
        
        for table_block in table_blocks:
            table_data = self._process_table_block(table_block, block_map)
            if table_data:
                tables.extend(table_data)
        
        return tables
    
    def _process_table_block(self, table_block: Dict, block_map: Dict) -> List[List[str]]:
        """Process a single table block from Textract"""
        table_data = []
        
        if 'Relationships' not in table_block:
            return table_data
        
        # Get table cells
        cell_blocks = []
        for relationship in table_block['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    if child_id in block_map:
                        child_block = block_map[child_id]
                        if child_block['BlockType'] == 'CELL':
                            cell_blocks.append(child_block)
        
        # Organize cells by row and column
        cells_by_position = {}
        for cell in cell_blocks:
            row_index = cell.get('RowIndex', 1) - 1
            col_index = cell.get('ColumnIndex', 1) - 1
            cell_text = self._get_cell_text(cell, block_map)
            
            if row_index not in cells_by_position:
                cells_by_position[row_index] = {}
            cells_by_position[row_index][col_index] = cell_text
        
        # Convert to list of lists
        if cells_by_position:
            max_row = max(cells_by_position.keys())
            for row_idx in range(max_row + 1):
                row_data = []
                if row_idx in cells_by_position:
                    max_col = max(cells_by_position[row_idx].keys()) if cells_by_position[row_idx] else -1
                    for col_idx in range(max_col + 1):
                        cell_value = cells_by_position[row_idx].get(col_idx, '')
                        row_data.append(cell_value)
                table_data.append(row_data)
        
        return table_data
    
    def _get_cell_text(self, cell_block: Dict, block_map: Dict) -> str:
        """Extract text from a table cell"""
        cell_text = []
        
        if 'Relationships' in cell_block:
            for relationship in cell_block['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        if child_id in block_map:
                            child_block = block_map[child_id]
                            if child_block['BlockType'] == 'WORD':
                                cell_text.append(child_block.get('Text', ''))
        
        return ' '.join(cell_text).strip()
    
    def _extract_key_value_pairs(self, response: Dict) -> Dict[str, str]:
        """Extract key-value pairs from Textract response"""
        key_value_pairs = {}
        
        # Create a map of block IDs to blocks
        block_map = {block['Id']: block for block in response.get('Blocks', [])}
        
        # Find key-value blocks
        key_blocks = [block for block in response.get('Blocks', []) if block['BlockType'] == 'KEY_VALUE_SET' and block.get('EntityTypes') == ['KEY']]
        
        for key_block in key_blocks:
            key_text = self._get_text_from_block(key_block, block_map)
            
            # Find associated value
            if 'Relationships' in key_block:
                for relationship in key_block['Relationships']:
                    if relationship['Type'] == 'VALUE':
                        for value_id in relationship['Ids']:
                            if value_id in block_map:
                                value_block = block_map[value_id]
                                value_text = self._get_text_from_block(value_block, block_map)
                                if key_text and value_text:
                                    key_value_pairs[key_text] = value_text
        
        return key_value_pairs
    
    def _get_text_from_block(self, block: Dict, block_map: Dict) -> str:
        """Extract text from a block using relationships"""
        text_parts = []
        
        if 'Relationships' in block:
            for relationship in block['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        if child_id in block_map:
                            child_block = block_map[child_id]
                            if child_block['BlockType'] == 'WORD':
                                text_parts.append(child_block.get('Text', ''))
        
        return ' '.join(text_parts).strip()
    
    def _process_carrier_data(self, carrier: str, text_content: str, tables: List[List[str]], 
                            key_value_pairs: Dict[str, str], pdf_path: str) -> Dict[str, Any]:
        """Process extracted data based on carrier type"""
        
        if carrier.lower() == 'hc':
            return self._process_hc_data(text_content, tables, key_value_pairs, pdf_path)
        elif carrier.lower() == 'hne':
            return self._process_hne_data(text_content, tables, key_value_pairs, pdf_path)
        elif carrier.lower() == 'humana':
            return self._process_humana_data(text_content, tables, key_value_pairs, pdf_path)
        else:
            return self._process_generic_data(text_content, tables, key_value_pairs, pdf_path)
    
    def _process_hc_data(self, text_content: str, tables: List[List[str]], 
                        key_value_pairs: Dict[str, str], pdf_path: str) -> Dict[str, Any]:
        """Process HC carrier-specific data"""
        self.logger.info("Processing HC commission data with Textract")
        
        # Extract statement date from text content (look for MM/YYYY pattern)
        statement_date = self._extract_hc_statement_date(text_content)
        
        # Process tables to extract commission entries
        entries = []
        for table in tables:
            if len(table) > 0:
                # Look for commission table structure
                table_entries = self._extract_hc_commission_entries(table, statement_date)
                entries.extend(table_entries)
        
        return {
            'carrier': 'hc',
            'statement_date': statement_date,
            'entries': entries,
            'total_amount': sum(entry.get('amount', 0) for entry in entries),
            'extraction_method': 'textract'
        }
    
    def _process_hne_data(self, text_content: str, tables: List[List[str]], 
                         key_value_pairs: Dict[str, str], pdf_path: str) -> Dict[str, Any]:
        """Process HNE carrier-specific data"""
        self.logger.info("Processing HNE commission data with Textract")
        
        # Extract statement date from text content
        statement_date = self._extract_hne_statement_date(text_content)
        
        # Process tables to extract commission entries
        entries = []
        for table in tables:
            if len(table) > 0:
                table_entries = self._extract_hne_commission_entries(table, statement_date)
                entries.extend(table_entries)
        
        return {
            'carrier': 'hne',
            'statement_date': statement_date,
            'entries': entries,
            'total_amount': sum(entry.get('amount', 0) for entry in entries),
            'extraction_method': 'textract'
        }
    
    def _process_humana_data(self, text_content: str, tables: List[List[str]], 
                           key_value_pairs: Dict[str, str], pdf_path: str) -> Dict[str, Any]:
        """Process Humana carrier-specific data"""
        self.logger.info("Processing Humana commission data with Textract")
        
        # Extract statement date from text content
        statement_date = self._extract_humana_statement_date(text_content)
        
        # Process tables to extract commission entries
        entries = []
        for table in tables:
            if len(table) > 0:
                table_entries = self._extract_humana_commission_entries(table, statement_date)
                entries.extend(table_entries)
        
        return {
            'carrier': 'humana',
            'statement_date': statement_date,
            'entries': entries,
            'total_amount': sum(entry.get('amount', 0) for entry in entries),
            'extraction_method': 'textract'
        }
    
    def _process_generic_data(self, text_content: str, tables: List[List[str]], 
                            key_value_pairs: Dict[str, str], pdf_path: str) -> Dict[str, Any]:
        """Process generic carrier data"""
        self.logger.info("Processing generic commission data with Textract")
        
        # Try to extract statement date from various patterns
        statement_date = self._extract_generic_statement_date(text_content)
        
        # Process all tables to find commission data
        entries = []
        for table in tables:
            if len(table) > 0:
                table_entries = self._extract_generic_commission_entries(table, statement_date)
                entries.extend(table_entries)
        
        return {
            'carrier': 'generic',
            'statement_date': statement_date,
            'entries': entries,
            'total_amount': sum(entry.get('amount', 0) for entry in entries),
            'extraction_method': 'textract'
        }
    
    def _extract_hc_statement_date(self, text_content: str) -> str:
        """Extract statement date for HC carrier (look for MM/YYYY pattern)"""
        # Look for MM/YYYY pattern in text
        pattern = r'(\d{2})/(\d{4})'
        matches = re.findall(pattern, text_content)
        
        if matches:
            # Find the most common MM/YYYY pattern
            from collections import Counter
            date_counts = Counter([f"{month}/{year}" for month, year in matches])
            most_common_date = date_counts.most_common(1)[0][0]
            
            # Convert to YYYY-MM-01 format
            month, year = most_common_date.split('/')
            return f"{year}-{month.zfill(2)}-01"
        
        return None
    
    def _extract_hne_statement_date(self, text_content: str) -> str:
        """Extract statement date for HNE carrier"""
        # Look for date patterns like M/D/YYYY
        pattern = r'(\d{1,2})/(\d{1,2})/(\d{4})'
        matches = re.findall(pattern, text_content)
        
        if matches:
            # Use the first valid date found
            month, day, year = matches[0]
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return None
    
    def _extract_humana_statement_date(self, text_content: str) -> str:
        """Extract statement date for Humana carrier"""
        # Look for patterns like "May 25" and convert to current year
        pattern = r'(\w+)\s+(\d{1,2})'
        matches = re.findall(pattern, text_content)
        
        if matches:
            month_name, day = matches[0]
            try:
                # Convert month name to number
                month_map = {
                    'january': 1, 'february': 2, 'march': 3, 'april': 4,
                    'may': 5, 'june': 6, 'july': 7, 'august': 8,
                    'september': 9, 'october': 10, 'november': 11, 'december': 12
                }
                month_num = month_map.get(month_name.lower())
                if month_num:
                    current_year = datetime.now().year
                    return f"{current_year}-{month_num:02d}-01"
            except:
                pass
        
        return None
    
    def _extract_generic_statement_date(self, text_content: str) -> str:
        """Extract statement date for generic carriers"""
        # Try multiple date patterns
        patterns = [
            r'(\d{2})/(\d{4})',  # MM/YYYY
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # M/D/YYYY
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # Month Day, Year
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_content)
            if matches:
                # Process first match based on pattern
                if len(matches[0]) == 2:  # MM/YYYY
                    month, year = matches[0]
                    return f"{year}-{month.zfill(2)}-01"
                elif len(matches[0]) == 3 and matches[0][2].isdigit():  # M/D/YYYY
                    month, day, year = matches[0]
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return None
    
    def _extract_hc_commission_entries(self, table: List[List[str]], statement_date: str) -> List[Dict[str, Any]]:
        """Extract commission entries from HC table"""
        entries = []
        
        if not table or len(table) < 2:
            return entries
        
        # Find header row and identify columns
        header_row = table[0]
        policy_col = None
        member_col = None
        employer_col = None
        amount_col = None
        
        for i, header in enumerate(header_row):
            if 'policy' in header.lower() or 'group' in header.lower():
                policy_col = i
            elif 'member' in header.lower() or 'name' in header.lower():
                member_col = i
            elif 'employer' in header.lower() or 'company' in header.lower():
                employer_col = i
            elif 'amount' in header.lower() or 'commission' in header.lower() or '$' in header:
                amount_col = i
        
        # Process data rows
        for row in table[1:]:
            # Check if we have valid column indices and row has enough columns
            valid_columns = [col for col in [policy_col, member_col, employer_col, amount_col] if col is not None]
            min_required_columns = max(valid_columns) + 1 if valid_columns else 0
            
            if len(row) >= min_required_columns:
                entry = {
                    'policy_number': row[policy_col] if policy_col is not None and policy_col < len(row) else '',
                    'member_name': row[member_col] if member_col is not None and member_col < len(row) else '',
                    'employer_name': row[employer_col] if employer_col is not None and employer_col < len(row) else '',
                    'amount': self._parse_amount(row[amount_col] if amount_col is not None and amount_col < len(row) else '0'),
                    'statement_date': statement_date,
                    'carrier': 'hc'
                }
                entries.append(entry)
        
        return entries
    
    def _extract_hne_commission_entries(self, table: List[List[str]], statement_date: str) -> List[Dict[str, Any]]:
        """Extract commission entries from HNE table"""
        entries = []
        
        if not table or len(table) < 2:
            return entries
        
        # Similar logic to HC but with HNE-specific column mapping
        header_row = table[0]
        policy_col = None
        amount_col = None
        
        for i, header in enumerate(header_row):
            header_lower = header.lower()
            if any(keyword in header_lower for keyword in ['contract id', 'policy', 'certificate', 'member id']):
                policy_col = i
            elif any(keyword in header_lower for keyword in ['payout amt', 'amount', 'commission', '$', 'rate']):
                amount_col = i
        
        # Process data rows
        for row in table[1:]:
            # Check if we have valid column indices and row has enough columns
            valid_columns = [col for col in [policy_col, amount_col] if col is not None]
            min_required_columns = max(valid_columns) + 1 if valid_columns else 0
            
            if len(row) >= min_required_columns:
                entry = {
                    'policy_number': row[policy_col] if policy_col is not None and policy_col < len(row) else '',
                    'amount': self._parse_amount(row[amount_col] if amount_col is not None and amount_col < len(row) else '0'),
                    'statement_date': statement_date,
                    'carrier': 'hne'
                }
                entries.append(entry)
        
        return entries
    
    def _extract_humana_commission_entries(self, table: List[List[str]], statement_date: str) -> List[Dict[str, Any]]:
        """Extract commission entries from Humana table"""
        entries = []
        
        if not table or len(table) < 2:
            return entries
        
        # Similar logic for Humana-specific structure
        header_row = table[0]
        policy_col = None
        member_col = None
        amount_col = None
        
        for i, header in enumerate(header_row):
            if 'member' in header.lower() or 'name' in header.lower():
                member_col = i
            elif 'amount' in header.lower() or 'commission' in header.lower() or '$' in header:
                amount_col = i
        
        # Process data rows
        for row in table[1:]:
            # Check if we have valid column indices and row has enough columns
            valid_columns = [col for col in [member_col, amount_col] if col is not None]
            min_required_columns = max(valid_columns) + 1 if valid_columns else 0
            
            if len(row) >= min_required_columns:
                entry = {
                    'policy_number': row[member_col] if member_col is not None and member_col < len(row) else '',  # Use member name as policy for Humana
                    'member_name': row[member_col] if member_col is not None and member_col < len(row) else '',
                    'commission_amount': self._parse_amount(row[amount_col] if amount_col is not None and amount_col < len(row) else '0'),
                    'statement_date': statement_date,
                    'carrier': 'humana'
                }
                entries.append(entry)
        
        return entries
    
    def _extract_generic_commission_entries(self, table: List[List[str]], statement_date: str) -> List[Dict[str, Any]]:
        """Extract commission entries from generic table"""
        entries = []
        
        if not table or len(table) < 2:
            return entries
        
        # Generic column detection
        header_row = table[0]
        policy_col = None
        amount_col = None
        
        for i, header in enumerate(header_row):
            if any(keyword in header.lower() for keyword in ['policy', 'member', 'name', 'id']):
                policy_col = i
            elif any(keyword in header.lower() for keyword in ['amount', 'commission', '$', 'total']):
                amount_col = i
        
        # Process data rows
        for row in table[1:]:
            # Check if we have valid column indices and row has enough columns
            valid_columns = [col for col in [policy_col, amount_col] if col is not None]
            min_required_columns = max(valid_columns) + 1 if valid_columns else 0
            
            if len(row) >= min_required_columns:
                entry = {
                    'policy_number': row[policy_col] if policy_col is not None and policy_col < len(row) else '',
                    'amount': self._parse_amount(row[amount_col] if amount_col is not None and amount_col < len(row) else '0'),
                    'statement_date': statement_date,
                    'carrier': 'generic'
                }
                entries.append(entry)
        
        return entries
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        try:
            # Remove currency symbols and commas
            clean_amount = re.sub(r'[,$]', '', str(amount_str))
            return float(clean_amount) if clean_amount else 0.0
        except:
            return 0.0