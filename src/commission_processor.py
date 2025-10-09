"""
Commission Processor Module
Handles parsing and extraction of commission data from various file formats
"""

import os
import pandas as pd
import pdfplumber
import PyPDF2
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from .llm_extraction_service import LLMExtractionService

class CommissionProcessor:
    """Main class for processing commission statements from multiple carriers"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['.pdf', '.xlsx', '.xls', '.csv']
        self.carrier_parsers = {
            'aetna': self._parse_aetna_pdf,
            'blue_cross': self._parse_blue_cross_pdf,
            'cigna': self._parse_cigna_pdf,
            'unitedhealth': self._parse_unitedhealth_pdf,
            'hne': self._parse_hne_pdf,
            'humana': self._parse_humana_pdf,
            'hc': self._parse_hc_pdf
        }
        self.enrollment_info = None
        self.llm_service = LLMExtractionService()
    
    def load_enrollment_info(self, docs_directory: str) -> None:
        """
        Load enrollment information from CSV file
        
        Args:
            docs_directory: Path to directory containing enrollment_info.csv
        """
        enrollment_file = os.path.join(docs_directory, 'enrollment_info.csv')
        
        if os.path.exists(enrollment_file):
            try:
                self.enrollment_info = pd.read_csv(enrollment_file)
                self.logger.info(f"Loaded enrollment info with {len(self.enrollment_info)} records")
            except Exception as e:
                self.logger.error(f"Error loading enrollment info: {str(e)}")
                self.enrollment_info = None
        else:
            self.logger.warning("No enrollment_info.csv found. Expected commissions will not be available.")
            self.enrollment_info = None
    
    def process_all_statements(self, docs_directory: str) -> Dict[str, Any]:
        """
        Process all commission statements in the specified directory
        
        Args:
            docs_directory: Path to directory containing commission statements
            
        Returns:
            Dictionary containing processed commission data by carrier
        """
        # Load enrollment info first
        self.load_enrollment_info(docs_directory)
        
        commission_data = {}
        
        if not os.path.exists(docs_directory):
            self.logger.error(f"Documents directory not found: {docs_directory}")
            return commission_data
        
        for filename in os.listdir(docs_directory):
            # Skip temporary files and hidden files
            if filename.startswith('~$') or filename.startswith('.'):
                continue
                
            file_path = os.path.join(docs_directory, filename)
            
            # Skip directories and unsupported files
            if os.path.isdir(file_path):
                continue
            
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in self.supported_formats:
                self.logger.warning(f"Unsupported file format: {filename}")
                continue
            
            # Skip enrollment and system files (same logic as file monitor)
            filename_lower = filename.lower()
            excluded_patterns = ['enrollment', 'llm_integration', 'readme', 'config']
            if any(pattern in filename_lower for pattern in excluded_patterns):
                self.logger.debug(f"Skipping excluded file: {filename}")
                continue
            
            # Determine carrier from filename
            carrier = self._identify_carrier(filename)
            if not carrier:
                # For unknown carriers, use filename as identifier and try AI extraction
                carrier = filename.split('_')[0].lower() if '_' in filename else os.path.splitext(filename)[0].lower()
                self.logger.info(f"Unknown carrier detected: {carrier}. Will use AI extraction for processing.")
            
            try:
                self.logger.info(f"Processing {carrier} commission statement: {filename}")
                
                if file_ext == '.pdf':
                    data = self._process_pdf(file_path, carrier)
                elif file_ext in ['.xlsx', '.xls']:
                    data = self._process_excel(file_path, carrier)
                elif file_ext == '.csv':
                    data = self._process_csv(file_path, carrier)
                
                if data:
                    # Enrich with enrollment info
                    data = self._enrich_with_enrollment_info(data, carrier)
                    commission_data[carrier] = data
                    self.logger.info(f"Successfully processed {carrier} statement")
                else:
                    self.logger.warning(f"No data extracted from {filename}")
                    
            except Exception as e:
                self.logger.error(f"Error processing {filename}: {str(e)}")
        
        return commission_data
    
    def _identify_carrier(self, filename: str) -> Optional[str]:
        """Identify the carrier based on filename"""
        filename_lower = filename.lower()
        
        if 'aetna' in filename_lower:
            return 'aetna'
        elif 'blue_cross' in filename_lower or 'bluecross' in filename_lower:
            return 'blue_cross'
        elif 'cigna' in filename_lower:
            return 'cigna'
        elif 'unitedhealth' in filename_lower or 'united_health' in filename_lower or 'uhc' in filename_lower:
            return 'unitedhealth'
        elif 'hne' in filename_lower:
            return 'hne'
        elif 'humana' in filename_lower:
            return 'humana'
        elif 'hc_commission' in filename_lower or filename_lower.startswith('hc_') or '_hc_' in filename_lower:
            return 'hc'
        
        return None
    
    def _process_pdf(self, file_path: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Process PDF commission statement"""
        parser = self.carrier_parsers.get(carrier)
        if not parser:
            return self._generic_pdf_parse(file_path, carrier)
        
        return parser(file_path)
    
    def _generic_pdf_parse(self, file_path: str, carrier: str) -> Dict[str, Any]:
        """Generic PDF parsing for unknown carrier formats"""
        data = {
            'carrier': carrier,
            'file_path': file_path,
            'commissions': [],
            'summary': {},
            'raw_text': ''
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                
                data['raw_text'] = full_text
                
                # Extract commission entries using LLM
                cost_estimate = self.llm_service.get_extraction_cost_estimate(len(full_text))
                self.logger.info(f"Estimated LLM extraction cost: ${cost_estimate['estimated_cost_usd']:.4f}")
                
                data['commissions'] = self.llm_service.extract_commission_entries(full_text, carrier)
                
                # Debug: log extracted entries
                self.logger.info(f"Extracted {len(data['commissions'])} commission entries for {carrier}")
                for i, entry in enumerate(data['commissions']):
                    self.logger.info(f"Entry {i+1}: Policy={entry.get('policy_number')}, Amount={entry.get('commission_amount')}, Member={entry.get('member_name')}")
                
                # Calculate summary statistics from extracted commissions
                if data['commissions']:
                    # Check for both 'amount' and 'commission_amount' fields
                    total_commission = sum(entry.get('commission_amount') or entry.get('amount', 0) for entry in data['commissions'])
                    data['summary'] = {
                        'total_commission': total_commission,
                        'count': len(data['commissions']),
                        'average_commission': total_commission / len(data['commissions']) if data['commissions'] else 0
                    }
                    # Also extract basic info from text
                    basic_info = self._extract_basic_info(full_text)
                    data['summary'].update(basic_info)
                else:
                    # Fallback to basic info extraction if no commissions found
                    data['summary'] = self._extract_basic_info(full_text)
                
        except Exception as e:
            self.logger.error(f"Error parsing PDF {file_path}: {str(e)}")
        
        return data
    
    def _parse_aetna_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse Aetna-specific PDF format"""
        data = self._generic_pdf_parse(file_path, 'aetna')
        
        # Add Aetna-specific parsing logic here
        # This would be customized based on Aetna's actual PDF format
        
        return data
    
    def _parse_blue_cross_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse Blue Cross-specific PDF format"""
        data = self._generic_pdf_parse(file_path, 'blue_cross')
        
        # Add Blue Cross-specific parsing logic here
        
        return data
    
    def _parse_cigna_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse Cigna-specific PDF format"""
        data = self._generic_pdf_parse(file_path, 'cigna')
        
        # Add Cigna-specific parsing logic here
        
        return data
    
    def _parse_unitedhealth_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse UnitedHealth-specific PDF format"""
        data = self._generic_pdf_parse(file_path, 'unitedhealth')
        
        # Add UnitedHealth-specific parsing logic here
        
        return data

    def _parse_hne_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse HNE-specific PDF format using carrier-specific LLM extraction"""
        data = {
            'carrier': 'hne',
            'file_path': file_path,
            'commissions': [],
            'summary': {},
            'raw_text': ''
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                
                data['raw_text'] = full_text
                
                # Use LLM service with HNE-specific extraction logic
                self.logger.info(f"Processing HNE commission statement with enhanced extraction")
                data['commissions'] = self.llm_service.extract_commission_entries(full_text, 'hne')
                
                # Debug: log extracted entries
                self.logger.info(f"Extracted {len(data['commissions'])} HNE commission entries")
                for i, entry in enumerate(data['commissions']):
                    self.logger.info(f"HNE Entry {i+1}: Policy={entry.get('policy_number')}, Amount={entry.get('commission_amount')}, Member={entry.get('member_name')}")
                
                # Calculate summary statistics
                if data['commissions']:
                    total_commission = sum(entry.get('commission_amount', 0) for entry in data['commissions'])
                    data['summary'] = {
                        'total_commission': total_commission,
                        'count': len(data['commissions']),
                        'average_commission': total_commission / len(data['commissions']) if data['commissions'] else 0
                    }
                else:
                    data['summary'] = {'total_commission': 0, 'count': 0, 'average_commission': 0}
                
        except Exception as e:
            self.logger.error(f"Error processing HNE PDF {file_path}: {str(e)}")
            
        return data

    def _parse_humana_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse Humana-specific PDF format using carrier-specific LLM extraction"""
        data = {
            'carrier': 'humana',
            'file_path': file_path,
            'commissions': [],
            'summary': {},
            'raw_text': ''
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                
                data['raw_text'] = full_text
                
                # Use LLM service with Humana-specific extraction logic
                self.logger.info(f"Processing Humana commission statement with enhanced extraction")
                data['commissions'] = self.llm_service.extract_commission_entries(full_text, 'humana')
                
                # Debug: log extracted entries
                self.logger.info(f"Extracted {len(data['commissions'])} Humana commission entries")
                for i, entry in enumerate(data['commissions']):
                    self.logger.info(f"Humana Entry {i+1}: Policy={entry.get('policy_number')}, Amount={entry.get('commission_amount')}, Member={entry.get('member_name')}")
                
                # Calculate summary statistics
                if data['commissions']:
                    total_commission = sum(entry.get('commission_amount', 0) for entry in data['commissions'])
                    data['summary'] = {
                        'total_commission': total_commission,
                        'count': len(data['commissions']),
                        'average_commission': total_commission / len(data['commissions']) if data['commissions'] else 0
                    }
                else:
                    data['summary'] = {'total_commission': 0, 'count': 0, 'average_commission': 0}
                
        except Exception as e:
            self.logger.error(f"Error processing Humana PDF {file_path}: {str(e)}")
            
        return data

    def _parse_hc_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse HC-specific PDF format using carrier-specific LLM extraction"""
        data = {
            'carrier': 'hc',
            'file_path': file_path,
            'commissions': [],
            'summary': {},
            'raw_text': ''
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                
                data['raw_text'] = full_text
                
                # Use LLM service with HC-specific extraction logic
                self.logger.info(f"Processing HC commission statement with enhanced extraction")
                data['commissions'] = self.llm_service.extract_commission_entries(full_text, 'hc')
                
                # Debug: log extracted entries
                self.logger.info(f"Extracted {len(data['commissions'])} HC commission entries")
                for i, entry in enumerate(data['commissions']):
                    self.logger.info(f"HC Entry {i+1}: Policy={entry.get('policy_number')}, Amount={entry.get('commission_amount')}, Member={entry.get('member_name')}")
                
                # Calculate summary statistics
                if data['commissions']:
                    total_commission = sum(entry.get('commission_amount', 0) for entry in data['commissions'])
                    data['summary'] = {
                        'total_commission': total_commission,
                        'count': len(data['commissions']),
                        'average_commission': total_commission / len(data['commissions']) if data['commissions'] else 0
                    }
                else:
                    data['summary'] = {'total_commission': 0, 'count': 0, 'average_commission': 0}
                
        except Exception as e:
            self.logger.error(f"Error processing HC PDF {file_path}: {str(e)}")
            
        return data
    
    def _extract_basic_info(self, text: str) -> Dict[str, Any]:
        """Extract basic information from text using regex patterns"""
        info = {}
        
        # Common patterns for commission statements
        patterns = {
            'statement_date': r'(?:statement|report)?\s*date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'period_start': r'period[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'period_end': r'(?:to|through)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'total_commission': r'total\s*commission[:\s]*\$?([\d,]+\.?\d*)',
            'agency_name': r'agency[:\s]+([A-Za-z\s]+)',
            'agent_id': r'(?:agent|producer)\s*(?:id|number)[:\s]+(\w+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info[key] = match.group(1).strip()
        
        return info
    

    
    def _process_excel(self, file_path: str, carrier: str) -> Dict[str, Any]:
        """Process Excel commission statement"""
        data = {
            'carrier': carrier,
            'file_path': file_path,
            'commissions': [],
            'summary': {}
        }
        
        try:
            df = pd.read_excel(file_path)
            
            # Convert DataFrame to commission entries
            # This would be customized based on each carrier's Excel format
            for _, row in df.iterrows():
                entry = {}
                for col in df.columns:
                    entry[col.lower().replace(' ', '_')] = row[col]
                data['commissions'].append(entry)
            
            # Calculate summary information
            if 'amount' in df.columns or 'commission' in df.columns:
                amount_col = 'amount' if 'amount' in df.columns else 'commission'
                data['summary']['total_commission'] = df[amount_col].sum()
                data['summary']['count'] = len(df)
            
        except Exception as e:
            self.logger.error(f"Error processing Excel file {file_path}: {str(e)}")
        
        return data
    
    def _process_csv(self, file_path: str, carrier: str) -> Dict[str, Any]:
        """Process CSV commission statement"""
        data = {
            'carrier': carrier,
            'file_path': file_path,
            'commissions': [],
            'summary': {}
        }
        
        try:
            df = pd.read_csv(file_path)
            
            # Convert DataFrame to commission entries
            for _, row in df.iterrows():
                entry = {}
                for col in df.columns:
                    entry[col.lower().replace(' ', '_')] = row[col]
                data['commissions'].append(entry)
            
            # Calculate summary information
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                # Assume the first numeric column is the commission amount
                amount_col = numeric_cols[0]
                data['summary']['total_commission'] = df[amount_col].sum()
                data['summary']['count'] = len(df)
            
        except Exception as e:
            self.logger.error(f"Error processing CSV file {file_path}: {str(e)}")
        
        return data
    
    def _enrich_with_enrollment_info(self, commission_data: Dict[str, Any], carrier: str) -> Dict[str, Any]:
        """
        Enrich commission data with enrollment information
        
        Args:
            commission_data: Commission data from statements
            carrier: Carrier name
            
        Returns:
            Enriched commission data
        """
        if self.enrollment_info is None:
            return commission_data
        
        carrier_enrollment = self.enrollment_info[
            self.enrollment_info['carrier'].str.lower() == carrier.lower()
        ].copy()
        
        if carrier_enrollment.empty:
            self.logger.warning(f"No enrollment info found for carrier: {carrier}")
            return commission_data
        
        # Create a mapping of policy numbers to enrollment info
        enrollment_map = {}
        for _, row in carrier_enrollment.iterrows():
            enrollment_map[str(row['policy_id']).upper()] = {
                'member_name': row['member_name'],
                'plan_name': row['plan_name'],
                'annual_premium': float(row['annual_premium']) if pd.notna(row['annual_premium']) else 0,
                'effective_date': row['effective_date'],
                'status': row['status'],
                'commission_type': row['commission_type'],
                'expected_commission': float(row['expected_commission']) if pd.notna(row['expected_commission']) else 0
            }
        
        # Enrich commission entries
        enriched_commissions = []
        for commission in commission_data.get('commissions', []):
            policy_num = str(commission.get('policy_number', '')).upper()
            
            if policy_num in enrollment_map:
                enrollment = enrollment_map[policy_num]
                commission.update({
                    'member_name': enrollment['member_name'],
                    'plan_name': enrollment['plan_name'],
                    'annual_premium': enrollment['annual_premium'],
                    'effective_date': enrollment['effective_date'],
                    'status': enrollment['status'],
                    'commission_type': enrollment['commission_type'],
                    'expected_commission': enrollment['expected_commission']
                })
            else:
                self.logger.warning(f"No enrollment info found for policy: {policy_num}")
                commission['expected_commission'] = 0  # Orphaned commissions have zero expected commission
            
            enriched_commissions.append(commission)
        
        commission_data['commissions'] = enriched_commissions
        
        # Update summary with expected totals
        if enriched_commissions:
            total_expected = sum(c.get('expected_commission', 0) for c in enriched_commissions)
            commission_data['summary']['total_expected_commission'] = total_expected
        
        return commission_data