#!/usr/bin/env python3
"""
Commission Reconciliation System
Comprehensive system for processing commission statements from multiple carriers using saved LandingAI responses.
Implements strict matching logic: both member ID and effective date must match exactly.
"""

import json
import pandas as pd
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import difflib
from collections import defaultdict


class CommissionReconciliationSystem:
    """
    Main system for processing commission reconciliation across multiple carriers.
    Uses only saved LandingAI JSON responses - no API calls.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.enrollment_df = None
        self.results = {}
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration for the system."""
        return {
            'landingai_responses_dir': 'landingai_system_responses',
            'enrollment_file': 'docs/enrollment_info.csv',
            'output_dir': 'commission_reconciliation_reports',
            'email_config': {
                'enabled': True,  # Set to True when email is configured
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': 'karthik2sekhar@gmail.com',  # Configure as needed
                'sender_password': 'abdkocpsoxdhqjmm',  # Configure as needed
                'recipients': ['karthik2sekhar@gmail.com']  # Configure as needed
            },
            'supported_carriers': {
                'hne': {
                    'name': 'Health New England',
                    'file_pattern': 'HNE_comm_system_response_*.json',
                    'table_identifier': 'Incentive ID : Broker Commission'
                },
                'humana': {
                    'name': 'Humana',
                    'file_pattern': 'Humana_commission_statement*.json',
                    'table_identifier': 'Product type'
                },
                'aetna': {
                    'name': 'Aetna',
                    'file_pattern': 'AETNA_comm_system_response_*.json',
                    'table_identifier': 'Commission Statement'
                },
                'cigna': {
                    'name': 'Cigna',
                    'file_pattern': 'CIGNA_comm_system_response_*.json',
                    'table_identifier': 'Agent Commission Report'
                },
                'unitedhealth': {
                    'name': 'UnitedHealth Group',
                    'file_pattern': 'UHG_comm_system_response_*.json',
                    'table_identifier': 'Commission Summary'
                }
                # Add other carriers here as their response files become available
            }
        }
    
    def load_enrollment_data(self) -> pd.DataFrame:
        """Load enrollment data from CSV file."""
        try:
            df = pd.read_csv(self.config['enrollment_file'])
            # Convert dates to consistent format for matching
            df['effective_date'] = pd.to_datetime(df['effective_date'], errors='coerce')
            df['statement_date'] = pd.to_datetime(df['statement_date'], errors='coerce')
            
            print(f"✅ Loaded {len(df)} total enrollment records")
            return df
            
        except Exception as e:
            print(f"❌ Error loading enrollment data: {e}")
            return pd.DataFrame()
    
    def find_carrier_response_files(self) -> Dict[str, List[str]]:
        """Find all available LandingAI response files for supported carriers."""
        response_files = {}
        responses_dir = Path(self.config['landingai_responses_dir'])
        
        if not responses_dir.exists():
            print(f"❌ LandingAI responses directory not found: {responses_dir}")
            return response_files
        
        for carrier_code, carrier_config in self.config['supported_carriers'].items():
            pattern = carrier_config['file_pattern']
            # Find files matching the pattern
            files = list(responses_dir.glob(pattern))
            if files:
                response_files[carrier_code] = [str(f) for f in files]
                print(f"✅ Found {len(files)} response file(s) for {carrier_config['name']}")
            else:
                print(f"⚠️ No response files found for {carrier_config['name']} (pattern: {pattern})")
        
        return response_files
    
    def extract_hne_commission_data(self, json_file: str) -> List[Dict[str, Any]]:
        """Extract commission entries from HNE JSON response using dynamic header mapping."""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading JSON file {json_file}: {e}")
            return []
        
        commission_entries = []
        table_identifier = self.config['supported_carriers']['hne']['table_identifier']
        
        # Find the commission table chunk
        for chunk in json_data.get('chunks', []):
            if chunk.get('type') == 'table' and table_identifier in chunk.get('markdown', ''):
                markdown = chunk['markdown']
                
                # Dynamic regex pattern that captures any number of columns
                row_pattern = r'<tr>(?:<td[^>]*>([^<]*)</td>)+</tr>'
                
                # More specific pattern to capture individual cells
                cell_pattern = r'<td[^>]*>([^<]*)</td>'
                
                # Find all table rows
                table_rows = re.findall(r'<tr>(.*?)</tr>', markdown)
                
                if not table_rows:
                    print("⚠️ No table rows found in markdown")
                    continue
                
                # Parse each row to extract cells
                parsed_rows = []
                for row_html in table_rows:
                    cells = re.findall(cell_pattern, row_html)
                    if cells:
                        parsed_rows.append(cells)
                
                if not parsed_rows:
                    print("⚠️ No cells extracted from table rows")
                    continue
                
                # Build column mapping from header row
                column_map = self._build_column_mapping(parsed_rows[0], 'hne')
                
                if not column_map:
                    print("⚠️ Could not build column mapping from header row")
                    continue
                
                print(f"📋 Column mapping: {column_map}")
                
                # Process data rows (skip header row)
                for row in parsed_rows[1:]:
                    # Skip rows that don't have enough columns or are invalid
                    if len(row) < len(column_map):
                        continue
                    
                    # Validate this is a data row (has member ID and effective date)
                    member_id_idx = column_map.get('member_id')
                    effective_date_idx = column_map.get('effective_date')
                    
                    if member_id_idx is None or effective_date_idx is None:
                        continue
                    
                    if (member_id_idx < len(row) and effective_date_idx < len(row) and
                        row[member_id_idx] and row[member_id_idx].strip() and
                        row[member_id_idx].strip() not in ['Member ID', ''] and
                        row[effective_date_idx] and '/' in row[effective_date_idx]):
                        
                        try:
                            # Extract commission amount using dynamic mapping
                            payout_idx = column_map.get('payout')
                            if payout_idx is None or payout_idx >= len(row):
                                print(f"⚠️ Payout column not found or out of range for row: {row}")
                                continue
                            
                            payout_str = row[payout_idx].replace(',', '').strip()
                            if payout_str and payout_str != 'Payout':
                                payout_amount = float(payout_str)
                            else:
                                continue
                            
                            # Build entry using dynamic column mapping
                            entry = {
                                'plan_id': self._safe_extract(row, column_map.get('plan_id')),
                                'transaction_id': self._safe_extract(row, column_map.get('transaction_id')),
                                'member_id': self._safe_extract(row, column_map.get('member_id')),
                                'effective_date': self._safe_extract(row, column_map.get('effective_date')),
                                'pbp_id': self._safe_extract(row, column_map.get('pbp_id')),
                                'last_name': self._safe_extract(row, column_map.get('last_name')),
                                'first_name': self._safe_extract(row, column_map.get('first_name')),
                                'broker_name': self._safe_extract(row, column_map.get('broker_name')),
                                'broker_id': self._safe_extract(row, column_map.get('broker_id')),
                                'commission_type': self._safe_extract(row, column_map.get('commission_type')),
                                'gross_amount': self._safe_extract_float(row, column_map.get('gross_amount')),
                                'net_amount': payout_amount,
                                'carrier': 'hne',
                                'source_file': json_file,
                                'extracted_from': 'landingai_json'
                            }
                            
                            commission_entries.append(entry)
                            
                        except (ValueError, IndexError) as e:
                            print(f"⚠️ Error parsing HNE row {row}: {e}")
                            continue
                
                print(f"✅ Extracted {len(commission_entries)} commission entries from HNE JSON")
                break
        
        return commission_entries
    
    def extract_commission_data_generic(self, json_file: str, carrier_code: str) -> List[Dict[str, Any]]:
        """Generic method to extract commission entries from any carrier's JSON response using dynamic header mapping."""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading JSON file {json_file}: {e}")
            return []
        
        commission_entries = []
        carrier_config = self.config['supported_carriers'].get(carrier_code)
        
        if not carrier_config:
            print(f"❌ No configuration found for carrier: {carrier_code}")
            return []
        
        # Handle Humana's unique structure
        if carrier_code.lower() == 'humana':
            return self._extract_humana_commission_data(json_data, json_file)
            
        # Handle other carriers with standard table structure
        table_identifier = carrier_config['table_identifier']
        
        # Find the commission table chunk
        for chunk in json_data.get('chunks', []):
            if chunk.get('type') == 'table' and table_identifier in chunk.get('markdown', ''):
                markdown = chunk['markdown']
                
                # More specific pattern to capture individual cells
                cell_pattern = r'<td[^>]*>([^<]*)</td>'
                
                # Find all table rows
                table_rows = re.findall(r'<tr>(.*?)</tr>', markdown)
                
                if not table_rows:
                    print("⚠️ No table rows found in markdown")
                    continue
                
                # Parse each row to extract cells
                parsed_rows = []
                for row_html in table_rows:
                    cells = re.findall(cell_pattern, row_html)
                    if cells:
                        parsed_rows.append(cells)
                
                if not parsed_rows:
                    print("⚠️ No cells extracted from table rows")
                    continue
                
                # Build column mapping from header row
                column_map = self._build_column_mapping(parsed_rows[0], carrier_code)
                
                if not column_map:
                    print("⚠️ Could not build column mapping from header row")
                    continue
                
                print(f"📋 Column mapping for {carrier_code.upper()}: {column_map}")
                
                # Process data rows (skip header row)
                for row in parsed_rows[1:]:
                    # Skip rows that don't have enough columns or are invalid
                    if len(row) < len(column_map):
                        continue
                    
                    # Validate this is a data row (has member ID and effective date)
                    member_id_idx = column_map.get('member_id')
                    effective_date_idx = column_map.get('effective_date')
                    
                    if member_id_idx is None or effective_date_idx is None:
                        continue
                    
                    if (member_id_idx < len(row) and effective_date_idx < len(row) and
                        row[member_id_idx] and row[member_id_idx].strip() and
                        row[member_id_idx].strip() not in ['Member ID', 'Policy ID', ''] and
                        row[effective_date_idx] and ('/' in row[effective_date_idx] or '-' in row[effective_date_idx])):
                        
                        try:
                            # Extract commission amount using dynamic mapping
                            payout_idx = column_map.get('payout')
                            if payout_idx is None or payout_idx >= len(row):
                                print(f"⚠️ Payout column not found or out of range for row: {row}")
                                continue
                            
                            payout_str = row[payout_idx].replace(',', '').strip()
                            if payout_str and payout_str not in ['Payout', 'Commission', 'Net Amount']:
                                payout_amount = float(payout_str)
                            else:
                                continue
                            
                            # Build entry using dynamic column mapping
                            entry = {
                                'plan_id': self._safe_extract(row, column_map.get('plan_id')),
                                'transaction_id': self._safe_extract(row, column_map.get('transaction_id')),
                                'member_id': self._safe_extract(row, column_map.get('member_id')),
                                'effective_date': self._safe_extract(row, column_map.get('effective_date')),
                                'pbp_id': self._safe_extract(row, column_map.get('pbp_id')),
                                'last_name': self._safe_extract(row, column_map.get('last_name')),
                                'first_name': self._safe_extract(row, column_map.get('first_name')),
                                'broker_name': self._safe_extract(row, column_map.get('broker_name')),
                                'broker_id': self._safe_extract(row, column_map.get('broker_id')),
                                'commission_type': self._safe_extract(row, column_map.get('commission_type')),
                                'gross_amount': self._safe_extract_float(row, column_map.get('gross_amount')),
                                'net_amount': payout_amount,
                                'carrier': carrier_code,
                                'source_file': json_file,
                                'extracted_from': 'landingai_json'
                            }
                            
                            commission_entries.append(entry)
                            
                        except (ValueError, IndexError) as e:
                            print(f"⚠️ Error parsing {carrier_code.upper()} row {row}: {e}")
                            continue
                
                print(f"✅ Extracted {len(commission_entries)} commission entries from {carrier_code.upper()} JSON")
                break
        
        return commission_entries
    
    def _extract_humana_commission_data(self, json_data: Dict[str, Any], json_file: str) -> List[Dict[str, Any]]:
        """Extract commission entries from Humana JSON response with unique structure."""
        commission_entries = []
        
        # Humana has a unique structure:
        # 1. Member information appears in text chunks before tables
        # 2. Commission data is in tables with "Product type" header
        # 3. Need to associate member info with subsequent commission tables
        # 4. Each member can have their own table immediately following their info
        
        chunks = json_data.get('chunks', [])
        
        print(f"🔍 Processing {len(chunks)} chunks from Humana JSON")
        
        # First pass: collect all member information and table positions
        members = []
        tables = []
        
        for i, chunk in enumerate(chunks):
            chunk_markdown = chunk.get('markdown', '')
            
            # Look for member information in text chunks
            member_match = re.search(r'([A-Z][a-zA-Z\'\s]+)\s+(\d{11}[A-Z])\s*\([^)]+\)\s*Effective\s+(\d{1,2}/\d{1,2}/\d{2,4})', chunk_markdown)
            if member_match:
                member_name = member_match.group(1).strip()
                member_id = member_match.group(2).strip()
                effective_date = member_match.group(3).strip()
                
                # Split name into first and last name
                name_parts = member_name.split()
                if len(name_parts) >= 3:  # "Last First Middle" format
                    last_name = name_parts[0]
                    first_name = ' '.join(name_parts[1:])
                elif len(name_parts) == 2:
                    last_name = name_parts[0]
                    first_name = name_parts[1]
                else:
                    last_name = member_name
                    first_name = ''
                
                member_info = {
                    'member_id': member_id,
                    'effective_date': effective_date,
                    'last_name': last_name,
                    'first_name': first_name,
                    'full_name': member_name,
                    'chunk_index': i
                }
                
                members.append(member_info)
                print(f"📋 Found member: {member_name} ({member_id}) - Effective: {effective_date}")
                # Don't continue here - chunk might also contain a table
            
            # Look for commission tables with "Product type" identifier
            if (chunk.get('type') == 'table' and 'Product type' in chunk_markdown):
                tables.append({
                    'chunk_index': i,
                    'markdown': chunk_markdown
                })
        
        print(f"📊 Found {len(members)} members and {len(tables)} commission tables")
        
        # Second pass: associate each table with the nearest preceding member
        for table in tables:
            table_index = table['chunk_index']
            
            # Find the closest member that appears before this table
            associated_member = None
            min_distance = float('inf')
            
            for member in members:
                if member['chunk_index'] < table_index:
                    distance = table_index - member['chunk_index']
                    if distance < min_distance:
                        min_distance = distance
                        associated_member = member
            
            if associated_member:
                print(f"📊 Processing table at chunk {table_index} for {associated_member['full_name']}")
                
                # Parse the table
                chunk_markdown = table['markdown']
                
                # Parse the HTML table
                cell_pattern = r'<td[^>]*>([^<]*)</td>'
                table_rows = re.findall(r'<tr>(.*?)</tr>', chunk_markdown)
                
                if not table_rows:
                    continue
                
                # Parse each row to extract cells
                parsed_rows = []
                for row_html in table_rows:
                    cells = re.findall(cell_pattern, row_html)
                    if cells:
                        parsed_rows.append(cells)
                
                if len(parsed_rows) < 2:  # Need header + at least one data row
                    continue
                
                # Build column mapping using similarity-based matching
                header_row = parsed_rows[0]
                column_mapping = self._build_column_mapping(header_row, 'humana')
                
                print(f"🎯 Humana column mapping: {column_mapping}")
                
                # Process data rows
                for row in parsed_rows[1:]:
                    # Skip empty rows or total rows
                    if (not row or len(row) < len(header_row) or
                        any(total_indicator in str(cell).lower() for cell in row 
                            for total_indicator in ['total', 'totals']) or
                        all(not cell.strip() for cell in row[:3])):  # Skip if first 3 cells are empty
                        continue
                    
                    try:
                        # Extract payout amount using column mapping
                        payout_idx = column_mapping.get('payout')
                        if payout_idx is None or payout_idx >= len(row):
                            continue
                        
                        payout_str = row[payout_idx].replace('$', '').replace(',', '').strip()
                        if not payout_str or payout_str.lower() in ['paid amount', '']:
                            continue
                            
                        payout_amount = float(payout_str)
                        
                        # Extract month and year for better date matching
                        month_paid = self._safe_extract(row, column_mapping.get('month_paid'))
                        year_info = self._safe_extract(row, column_mapping.get('year'))
                        
                        # Convert Humana's month/year format to standard effective date
                        commission_effective_date = self._convert_humana_date(month_paid, year_info)
                        
                        # Extract other fields using similarity mapping
                        entry = {
                            'plan_id': self._safe_extract(row, column_mapping.get('plan_id')),
                            'product_type': self._safe_extract(row, column_mapping.get('product_type')),
                            'product_code': self._safe_extract(row, column_mapping.get('product_code')),
                            'month_paid': month_paid,
                            'year': year_info,
                            'rate': self._safe_extract_float(row, column_mapping.get('rate')),
                            'comments': self._safe_extract(row, column_mapping.get('comments')),
                            
                            # Member information from associated member
                            'member_id': associated_member['member_id'],
                            'effective_date': commission_effective_date or associated_member['effective_date'],
                            'last_name': associated_member['last_name'],
                            'first_name': associated_member['first_name'],
                            'enrollment_effective_date': associated_member['effective_date'],  # Keep original for reference
                            
                            # Commission details
                            'net_amount': payout_amount,
                            'payout': payout_amount,
                            'carrier': 'humana',
                            'source_file': json_file,
                            'extracted_from': 'landingai_json'
                        }
                        
                        commission_entries.append(entry)
                        
                    except (ValueError, IndexError) as e:
                        print(f"⚠️ Error parsing Humana commission row {row}: {e}")
                        continue
        
        print(f"✅ Extracted {len(commission_entries)} commission entries from Humana JSON")
        return commission_entries
    
    def _convert_humana_date(self, month_paid: str, year_info: str) -> Optional[str]:
        """Convert Humana's month/year format to effective date for matching."""
        if not month_paid or not year_info:
            return None
        
        try:
            # Humana format: "MAY 25" means May 2025
            # Parse month name and year
            month_year = month_paid.strip().upper()
            year_code = year_info.strip().upper()
            
            # Map month abbreviations
            month_map = {
                'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
                'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
                'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
            }
            
            # Extract month from "MAY 25" format
            if ' ' in month_year:
                month_part = month_year.split()[0]
                year_part = month_year.split()[1]
                
                if month_part in month_map:
                    month_num = month_map[month_part]
                    # Convert 2-digit year to 4-digit
                    if len(year_part) == 2:
                        year_full = f"20{year_part}"
                    else:
                        year_full = year_part
                    
                    # Return in format matching enrollment data (M/D/YYYY)
                    return f"{int(month_num)}/1/{year_full}"
            
        except Exception as e:
            print(f"⚠️ Error converting Humana date '{month_paid}' / '{year_info}': {e}")
            
        return None
    
    def _build_column_mapping(self, header_row: List[str], carrier_code: str = '') -> Dict[str, int]:
        """Build mapping from column names to their indices using similarity-based matching."""
        column_map = {}
        
        # Check if this is a title row (like HNE's "Incentive ID : Broker Commission")
        if len(header_row) == 1 or any('incentive' in str(header).lower() for header in header_row):
            # Use predefined mapping for HNE table structure
            if carrier_code.lower() == 'hne':
                return {
                    'plan_id': 0,          # H2737
                    'transaction_id': 1,    # 9P87YX0QG32
                    'member_id': 2,         # 90004932901
                    'effective_date': 3,    # 2/1/2025
                    'pbp_id': 4,           # 001
                    'last_name': 5,        # Matthess
                    'first_name': 6,       # Albert
                    'broker_name': 7,      # Katherine Beth Evans
                    'broker_id': 8,        # 15668354
                    'commission_type': 10,  # NEW (skip column 9 which is *)
                    'gross_amount': 11,     # 626.00
                    'payout': 12           # 626.00
                }
        
        # Define target field names with semantic keywords for similarity matching
        target_fields = {
            'plan_id': ['plan', 'product', 'scheme'],
            'transaction_id': ['transaction', 'trans', 'reference', 'ref', 'confirmation', 'confirm'],
            'member_id': ['member', 'policy', 'subscriber', 'customer', 'client', 'enrollee', 'participant'],
            'effective_date': ['effective', 'start', 'begin', 'commence', 'date', 'activation'],
            'pbp_id': ['pbp', 'benefit', 'plan', 'package'],
            'last_name': ['last', 'surname', 'family', 'lastname'],
            'first_name': ['first', 'given', 'forename', 'firstname'],
            'broker_name': ['broker', 'agent', 'representative', 'rep', 'advisor'],
            'broker_id': ['broker', 'agent', 'representative', 'rep', 'advisor'],
            'commission_type': ['type', 'category', 'class', 'kind'],
            'gross_amount': ['gross', 'rate', 'base', 'initial'],
            'payout': ['payout', 'net', 'commission', 'payment', 'amount', 'total', 'final', 'paid amount'],
            
            # Humana-specific fields
            'product_type': ['product', 'type'],
            'product_code': ['product', 'code'],
            'month_paid': ['month', 'paid', 'date'],
            'year': ['year'],
            'rate': ['rate'],
            'comments': ['comments', 'comment', 'note', 'notes']
        }
        
        # Special handling for Humana's specific column structure
        if carrier_code.lower() == 'humana':
            # Humana has predictable column structure: Product type, Product code, Month paid/ Paid to date, Year, Rate, Paid amount, Comments
            humana_mapping = {}
            for idx, header in enumerate(header_row):
                header_lower = header.lower()
                if 'product type' in header_lower:
                    humana_mapping['product_type'] = idx
                elif 'product code' in header_lower:
                    humana_mapping['product_code'] = idx
                elif 'month paid' in header_lower or 'paid to date' in header_lower:
                    humana_mapping['month_paid'] = idx
                elif header_lower == 'year':
                    humana_mapping['year'] = idx
                elif header_lower == 'rate':
                    humana_mapping['rate'] = idx
                elif 'paid amount' in header_lower and 'month' not in header_lower:
                    humana_mapping['payout'] = idx
                elif 'comment' in header_lower:
                    humana_mapping['comments'] = idx
            
            print(f"🎯 Humana specific column mapping: {humana_mapping}")
            return humana_mapping
        
        # Use similarity-based matching to find best column for each field
        column_map = self._find_similar_columns(header_row, target_fields)
        
        # Special handling for payout field - check if any column contains payment-related keywords
        if 'payout' not in column_map:
            payout_keywords = ['payout', 'net', 'commission', 'payment', 'amount', 'pay', 'total', 'final']
            for idx, header in enumerate(header_row):
                if idx not in column_map.values():  # Don't reassign already used columns
                    header_lower = header.lower()
                    for keyword in payout_keywords:
                        if keyword in header_lower:
                            column_map['payout'] = idx
                            print(f"🎯 Special match for 'payout' to column {idx}: '{header}' (contains '{keyword}')")
                            break
                    if 'payout' in column_map:
                        break
        
        # Verify we have the essential columns
        essential_columns = ['member_id', 'effective_date', 'payout']
        missing_columns = [col for col in essential_columns if col not in column_map]
        
        if missing_columns:
            print(f"⚠️ Missing essential columns after similarity matching: {missing_columns}")
            print(f"📋 Available headers: {header_row}")
            print(f"📋 Similarity results: {column_map}")
            return {}
        
        return column_map
    
    def _find_similar_columns(self, header_row: List[str], target_fields: Dict[str, List[str]]) -> Dict[str, int]:
        """Find the best matching column for each target field using similarity scoring."""
        column_map = {}
        used_columns = set()  # Track used columns to avoid duplicates
        
        # Pre-identify payout columns to protect them from other field assignments
        payout_keywords = ['payout', 'net', 'commission', 'payment', 'amount', 'pay', 'total', 'final']
        protected_payout_columns = set()
        
        for idx, header in enumerate(header_row):
            header_lower = header.lower().replace('_', ' ').replace('-', ' ').replace('$', '').strip()
            for keyword in payout_keywords:
                if keyword in header_lower:
                    protected_payout_columns.add(idx)
                    break
        
        # Calculate similarity scores for each target field
        field_scores = {}
        for field_name, keywords in target_fields.items():
            field_scores[field_name] = []
            
            for idx, header in enumerate(header_row):
                if idx in used_columns:
                    continue
                
                # For non-payout fields, exclude protected payout columns
                if field_name != 'payout' and idx in protected_payout_columns:
                    continue
                
                # Calculate similarity score for this header against field keywords
                score = self._calculate_similarity_score(header, keywords)
                field_scores[field_name].append((idx, header, score))
            
            # Sort by score (highest first)
            field_scores[field_name].sort(key=lambda x: x[2], reverse=True)
        
        # Prioritize payout field assignment first
        field_order = ['payout'] + [f for f in target_fields.keys() if f != 'payout']
        
        # Assign columns to fields based on priority and highest scores
        for field_name in field_order:
            if field_scores[field_name]:
                # Find the best available column for this field
                for idx, header, score in field_scores[field_name]:
                    if idx not in used_columns and score > 0.3:  # Minimum similarity threshold
                        column_map[field_name] = idx
                        used_columns.add(idx)
                        print(f"🎯 Matched '{field_name}' to column {idx}: '{header}' (similarity: {score:.2f})")
                        break
        
        return column_map
    
    def _calculate_similarity_score(self, header: str, keywords: List[str]) -> float:
        """Calculate similarity score between a header and a list of keywords."""
        if not header or not keywords:
            return 0.0
        
        header_normalized = header.lower().strip().replace('_', ' ').replace('-', ' ')
        
        # Remove common words that don't add meaning
        stop_words = {'id', 'number', 'num', 'no', '#'}
        header_words = [word for word in header_normalized.split() if word not in stop_words]
        
        max_score = 0.0
        
        for keyword in keywords:
            keyword_normalized = keyword.lower().strip()
            
            # Exact match bonus
            if keyword_normalized in header_normalized:
                max_score = max(max_score, 1.0)
                continue
            
            # Word-level matching
            for header_word in header_words:
                # Exact word match
                if header_word == keyword_normalized:
                    max_score = max(max_score, 0.9)
                    continue
                
                # Substring matching
                if keyword_normalized in header_word or header_word in keyword_normalized:
                    max_score = max(max_score, 0.8)
                    continue
                
                # Fuzzy string similarity using difflib
                similarity = difflib.SequenceMatcher(None, header_word, keyword_normalized).ratio()
                
                # Boost score for longer matches
                length_bonus = min(len(header_word), len(keyword_normalized)) / 10.0
                adjusted_similarity = similarity + (length_bonus * 0.1)
                
                max_score = max(max_score, adjusted_similarity)
        
        # Additional scoring for common patterns
        if any(keyword in header_normalized for keyword in keywords):
            max_score = max(max_score, 0.7)
        
        return min(max_score, 1.0)  # Cap at 1.0
    
    def _safe_extract(self, row: List[str], index: Optional[int]) -> str:
        """Safely extract string value from row at given index."""
        if index is None or index >= len(row):
            return ""
        return row[index].strip()
    
    def _safe_extract_float(self, row: List[str], index: Optional[int]) -> float:
        """Safely extract float value from row at given index."""
        if index is None or index >= len(row):
            return 0.0
        
        value_str = row[index].replace(',', '').strip()
        try:
            return float(value_str) if value_str else 0.0
        except ValueError:
            return 0.0
    
    def convert_effective_date(self, date_str: str) -> Optional[datetime]:
        """Convert effective date from commission table format to datetime."""
        try:
            # Commission table format: "2/1/2025"
            return datetime.strptime(date_str, "%m/%d/%Y")
        except ValueError:
            try:
                # Try alternative format
                return datetime.strptime(date_str, "%m/%d/%y")
            except ValueError:
                print(f"⚠️ Could not parse date: {date_str}")
                return None
    
    def find_enrollment_match(self, commission_entry: Dict[str, Any], carrier_enrollment_df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Find matching enrollment record for a commission entry.
        CRITICAL: Requires EXACT member ID and statement date match for all carriers.
        """
        member_id = commission_entry['member_id']
        carrier = commission_entry.get('carrier', '').lower()
        
        # For commission reconciliation, we match based on statement date, not effective date
        commission_date = self.convert_effective_date(commission_entry['effective_date'])
        
        if not commission_date:
            return None
        
        # Look for exact member ID match
        member_matches = carrier_enrollment_df[carrier_enrollment_df['policy_id'].astype(str) == member_id]
        
        if len(member_matches) == 0:
            return None
        
        # From member matches, find EXACT statement date match (same day)
        for _, enrollment_record in member_matches.iterrows():
            enrollment_statement_date = enrollment_record.get('statement_date')
            
            if pd.isna(enrollment_statement_date):
                continue
            
            enrollment_statement_datetime = pd.to_datetime(enrollment_statement_date, errors='coerce')
            if not enrollment_statement_datetime:
                continue
            
            # Require EXACT statement date match (same day) - this is the critical business rule
            if commission_date.date() == enrollment_statement_datetime.date():
                return enrollment_record.to_dict()
        
        # No exact match found - this ensures strict reconciliation
        return None
    

    def process_carrier_commissions(self, carrier_code: str, response_files: List[str]) -> Dict[str, Any]:
        """Process commission reconciliation for a specific carrier."""
        print(f"\n🏥 Processing {self.config['supported_carriers'][carrier_code]['name']} Commissions")
        print("="*70)
        
        # Get enrollment data for this carrier
        carrier_enrollment_df = self.enrollment_df[
            self.enrollment_df['carrier'].str.lower() == carrier_code
        ].copy()
        
        print(f"📊 Found {len(carrier_enrollment_df)} enrollment records for {carrier_code.upper()}")
        
        all_commission_entries = []
        matched_entries = []
        unmatched_entries = []
        
        # Process each response file for this carrier
        for response_file in response_files:
            print(f"📄 Processing file: {os.path.basename(response_file)}")
            
            # Extract commission data using generic method
            commission_entries = self.extract_commission_data_generic(response_file, carrier_code)
            
            all_commission_entries.extend(commission_entries)
            
            # Process each commission entry for matching
            for commission_entry in commission_entries:
                enrollment_match = self.find_enrollment_match(commission_entry, carrier_enrollment_df)
                
                if enrollment_match:
                    matched_entry = {
                        'commission_data': commission_entry,
                        'enrollment_data': enrollment_match,
                        'match_type': 'exact_member_id_and_date',
                        'match_confidence': 'high'
                    }
                    matched_entries.append(matched_entry)
                else:
                    unmatched_entry = {
                        'commission_data': commission_entry,
                        'reason': 'no_exact_enrollment_match_found',
                        'possible_issues': [
                            'Member ID not in enrollment data',
                            'Effective date mismatch',
                            'Member enrolled in different year'
                        ]
                    }
                    unmatched_entries.append(unmatched_entry)
        
        # Calculate financial totals
        total_commission = sum(entry['net_amount'] for entry in all_commission_entries)
        matched_commission = sum(entry['commission_data']['net_amount'] for entry in matched_entries)
        unmatched_commission = sum(entry['commission_data']['net_amount'] for entry in unmatched_entries)
        
        carrier_results = {
            'carrier_code': carrier_code,
            'carrier_name': self.config['supported_carriers'][carrier_code]['name'],
            'processing_timestamp': datetime.now().isoformat(),
            'source_files': response_files,
            'enrollment_records_available': len(carrier_enrollment_df),
            'summary': {
                'total_extracted': len(all_commission_entries),
                'total_matched': len(matched_entries),
                'total_unmatched': len(unmatched_entries),
                'match_percentage': (len(matched_entries) / len(all_commission_entries)) * 100 if all_commission_entries else 0,
                'total_commission': total_commission,
                'matched_commission': matched_commission,
                'unmatched_commission': unmatched_commission
            },
            'matched_entries': matched_entries,
            'unmatched_entries': unmatched_entries,
            'all_commission_entries': all_commission_entries
        }
        
        return carrier_results
    
    def generate_carrier_report(self, carrier_results: Dict[str, Any]) -> str:
        """Generate detailed report for a specific carrier."""
        report = []
        
        report.append(f"{'='*80}")
        report.append(f"🎯 {carrier_results['carrier_name'].upper()} COMMISSION RECONCILIATION REPORT")
        report.append(f"{'='*80}")
        report.append(f"📅 Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📄 Source Files: {len(carrier_results['source_files'])}")
        for file in carrier_results['source_files']:
            report.append(f"   - {os.path.basename(file)}")
        
        summary = carrier_results['summary']
        report.append(f"\n📊 EXTRACTION & MATCHING RESULTS:")
        report.append(f"   Total Commission Entries Extracted: {summary['total_extracted']}")
        report.append(f"   Successfully Matched: {summary['total_matched']}")
        report.append(f"   Unmatched Entries: {summary['total_unmatched']}")
        report.append(f"   Match Rate: {summary['match_percentage']:.1f}%")
        report.append(f"   Enrollment Records Available: {carrier_results['enrollment_records_available']}")
        
        report.append(f"\n💰 FINANCIAL SUMMARY:")
        report.append(f"   Total Commission Amount: ${summary['total_commission']:.2f}")
        report.append(f"   Matched Commission Amount: ${summary['matched_commission']:.2f}")
        report.append(f"   Unmatched Commission Amount: ${summary['unmatched_commission']:.2f}")
        
        # Matched entries details
        if carrier_results['matched_entries']:
            report.append(f"\n✅ MATCHED ENTRIES ({len(carrier_results['matched_entries'])}):")
            for i, match in enumerate(carrier_results['matched_entries'], 1):
                comm = match['commission_data']
                enroll = match['enrollment_data']
                report.append(f"   {i}. {comm['first_name']} {comm['last_name']} (ID: {comm['member_id']})")
                report.append(f"      📈 Commission: ${comm['net_amount']:.2f}")
                report.append(f"      📋 Enrollment Expected: ${enroll.get('expected_commission', 0):.2f}")
                report.append(f"      📅 Effective Date: {comm['effective_date']}")
                report.append(f"      🏥 Plan: {enroll.get('plan_name', 'N/A')}")
                report.append(f"      📊 Status: {enroll.get('status', 'N/A')} | Type: {enroll.get('commission_type', 'N/A')}")
                report.append("")
        
        # Unmatched entries details
        if carrier_results['unmatched_entries']:
            report.append(f"\n❌ UNMATCHED ENTRIES ({len(carrier_results['unmatched_entries'])}):")
            for i, unmatch in enumerate(carrier_results['unmatched_entries'], 1):
                comm = unmatch['commission_data']
                report.append(f"   {i}. {comm['first_name']} {comm['last_name']} (ID: {comm['member_id']})")
                report.append(f"      💰 Commission: ${comm['net_amount']:.2f}")
                report.append(f"      📅 Effective Date: {comm['effective_date']}")
                report.append(f"      ❓ Reason: {unmatch['reason']}")
                report.append("")
        
        # Assessment
        match_percentage = summary['match_percentage']
        report.append(f"\n🎯 RECONCILIATION ASSESSMENT:")
        if match_percentage >= 90:
            report.append("   🎉 EXCELLENT: High matching rate - minimal issues detected")
        elif match_percentage >= 75:
            report.append("   👍 GOOD: Acceptable matching rate - minor investigation needed")
        elif match_percentage >= 50:
            report.append("   ⚠️ MODERATE: Several unmatched entries - investigation required")
        else:
            report.append("   🚨 CRITICAL: Low matching rate - immediate attention required")
        
        report.append(f"   Match Rate: {match_percentage:.1f}%")
        
        # Action items
        if carrier_results['unmatched_entries']:
            report.append(f"\n📋 RECOMMENDED ACTIONS:")
            report.append("   1. Verify enrollment data contains all expected 2025 records")
            report.append("   2. Check for member ID formatting discrepancies")
            report.append("   3. Confirm effective dates in enrollment match commission statement dates")
            report.append("   4. Review if unmatched members have pending enrollment updates")
        
        report.append(f"\n{'='*80}")
        
        return "\n".join(report)
    
    def create_email_body(self, all_results: Dict[str, Dict[str, Any]]) -> Tuple[str, str]:
        """Create email subject and body for commission reconciliation summary."""
        # Calculate overall summary
        total_carriers = len(all_results)
        total_extracted = sum(result['summary']['total_extracted'] for result in all_results.values())
        total_matched = sum(result['summary']['total_matched'] for result in all_results.values())
        total_unmatched = sum(result['summary']['total_unmatched'] for result in all_results.values())
        overall_match_rate = (total_matched / total_extracted) * 100 if total_extracted > 0 else 0
        total_commission = sum(result['summary']['total_commission'] for result in all_results.values())
        
        # Create subject
        date_str = datetime.now().strftime('%Y-%m-%d')
        subject = f"Commission Reconciliation Report - {date_str} - {overall_match_rate:.1f}% Match Rate"
        
        # Create body
        body = []
        body.append("Commission Reconciliation Daily Report")
        body.append("="*50)
        body.append(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        body.append(f"Processing Method: Saved LandingAI Responses (No API Calls)")
        body.append("")
        
        body.append("OVERALL SUMMARY:")
        body.append(f"  Carriers Processed: {total_carriers}")
        body.append(f"  Total Commission Entries: {total_extracted}")
        body.append(f"  Successfully Matched: {total_matched}")
        body.append(f"  Unmatched Entries: {total_unmatched}")
        body.append(f"  Overall Match Rate: {overall_match_rate:.1f}%")
        body.append(f"  Total Commission Amount: ${total_commission:.2f}")
        body.append("")
        
        # Per carrier summary
        body.append("CARRIER BREAKDOWN:")
        for carrier_code, result in all_results.items():
            summary = result['summary']
            body.append(f"  {result['carrier_name']}:")
            body.append(f"    Entries: {summary['total_extracted']}")
            body.append(f"    Matched: {summary['total_matched']} ({summary['match_percentage']:.1f}%)")
            body.append(f"    Commission: ${summary['total_commission']:.2f}")
            body.append("")
        
        # Issues requiring attention
        issues_found = []
        for carrier_code, result in all_results.items():
            if result['summary']['match_percentage'] < 90:
                issues_found.append(f"  - {result['carrier_name']}: {result['summary']['match_percentage']:.1f}% match rate")
        
        if issues_found:
            body.append("ISSUES REQUIRING ATTENTION:")
            body.extend(issues_found)
            body.append("")
            body.append("Please review detailed reports for investigation steps.")
        else:
            body.append("STATUS: All carriers show excellent match rates (>90%)")
        
        body.append("")
        body.append("Detailed reports are attached to this email.")
        body.append("")
        body.append("This report was generated automatically using the Commission Reconciliation System.")
        
        return subject, "\n".join(body)
    
    def send_email_report(self, all_results: Dict[str, Dict[str, Any]], report_files: List[str]):
        """Send email report with attachments."""
        email_config = self.config['email_config']
        
        if not email_config.get('enabled', False):
            print("📧 Email not configured - skipping email report")
            return
        
        try:
            # Create email content
            subject, body = self.create_email_body(all_results)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = ', '.join(email_config['recipients'])
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            for report_file in report_files:
                with open(report_file, 'rb') as f:
                    attachment = MIMEApplication(f.read(), _subtype='txt')
                    attachment.add_header('Content-Disposition', 'attachment', 
                                        filename=os.path.basename(report_file))
                    msg.attach(attachment)
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Email report sent successfully to {len(email_config['recipients'])} recipients")
            
        except Exception as e:
            print(f"❌ Error sending email report: {e}")
    
    def save_reports(self, all_results: Dict[str, Dict[str, Any]]) -> List[str]:
        """Save detailed reports to files."""
        # Create output directory
        output_dir = Path(self.config['output_dir'])
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_files = []
        
        # Save individual carrier reports
        for carrier_code, result in all_results.items():
            # Text report
            report_content = self.generate_carrier_report(result)
            report_file = output_dir / f"{carrier_code}_commission_report_{timestamp}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            report_files.append(str(report_file))
            
            # JSON data
            json_file = output_dir / f"{carrier_code}_commission_data_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"📄 Saved reports for {result['carrier_name']}: {report_file.name}")
        
        # Save combined summary
        summary_file = output_dir / f"commission_reconciliation_summary_{timestamp}.json"
        combined_summary = {
            'processing_timestamp': datetime.now().isoformat(),
            'overall_summary': {
                'total_carriers': len(all_results),
                'total_extracted': sum(r['summary']['total_extracted'] for r in all_results.values()),
                'total_matched': sum(r['summary']['total_matched'] for r in all_results.values()),
                'total_unmatched': sum(r['summary']['total_unmatched'] for r in all_results.values()),
                'total_commission': sum(r['summary']['total_commission'] for r in all_results.values())
            },
            'carrier_results': all_results
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(combined_summary, f, indent=2, ensure_ascii=False, default=str)
        
        return report_files
    
    def run_full_reconciliation(self):
        """Run complete commission reconciliation process for all available carriers."""
        print("🚀 Starting Commission Reconciliation System")
        print("="*80)
        print("📋 Configuration:")
        print(f"   LandingAI Responses Directory: {self.config['landingai_responses_dir']}")
        print(f"   Enrollment Data: {self.config['enrollment_file']}")
        print(f"   Output Directory: {self.config['output_dir']}")
        print(f"   Email Enabled: {self.config['email_config'].get('enabled', False)}")
        print("="*80)
        
        # Load enrollment data
        print("\n📊 Loading enrollment data...")
        self.enrollment_df = self.load_enrollment_data()
        if self.enrollment_df.empty:
            print("❌ Cannot proceed without enrollment data")
            return
        
        # Find available response files
        print("\n🔍 Scanning for LandingAI response files...")
        response_files = self.find_carrier_response_files()
        
        if not response_files:
            print("❌ No carrier response files found")
            return
        
        # Process each carrier
        all_results = {}
        for carrier_code, files in response_files.items():
            carrier_results = self.process_carrier_commissions(carrier_code, files)
            all_results[carrier_code] = carrier_results
            self.results[carrier_code] = carrier_results
        
        # Generate and save reports
        print(f"\n📄 Generating reports...")
        report_files = self.save_reports(all_results)
        
        # Send email if configured
        if self.config['email_config'].get('enabled', False):
            print(f"\n📧 Sending email reports...")
            self.send_email_report(all_results, report_files)
        
        # Print final summary
        self._print_final_summary(all_results)
        
        print(f"\n✅ Commission reconciliation completed successfully!")
        print(f"📄 Reports saved to: {self.config['output_dir']}")
    
    def _print_final_summary(self, all_results: Dict[str, Dict[str, Any]]):
        """Print final summary of all processing."""
        print(f"\n{'='*80}")
        print("🎯 FINAL RECONCILIATION SUMMARY")
        print("="*80)
        
        total_extracted = sum(r['summary']['total_extracted'] for r in all_results.values())
        total_matched = sum(r['summary']['total_matched'] for r in all_results.values())
        total_unmatched = sum(r['summary']['total_unmatched'] for r in all_results.values())
        total_commission = sum(r['summary']['total_commission'] for r in all_results.values())
        overall_match_rate = (total_matched / total_extracted) * 100 if total_extracted > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Carriers Processed: {len(all_results)}")
        print(f"   Total Commission Entries: {total_extracted}")
        print(f"   Successfully Matched: {total_matched}")
        print(f"   Unmatched Entries: {total_unmatched}")
        print(f"   Overall Match Rate: {overall_match_rate:.1f}%")
        print(f"   Total Commission Amount: ${total_commission:.2f}")
        
        print(f"\n🏥 CARRIER BREAKDOWN:")
        for carrier_code, result in all_results.items():
            summary = result['summary']
            status_icon = "✅" if summary['match_percentage'] >= 90 else "⚠️" if summary['match_percentage'] >= 75 else "🚨"
            print(f"   {status_icon} {result['carrier_name']}:")
            print(f"      Match Rate: {summary['match_percentage']:.1f}% ({summary['total_matched']}/{summary['total_extracted']})")
            print(f"      Commission: ${summary['total_commission']:.2f}")
        
        # Overall assessment
        print(f"\n🎯 SYSTEM ASSESSMENT:")
        if overall_match_rate >= 95:
            print("   🎉 EXCELLENT: System operating optimally with minimal exceptions")
        elif overall_match_rate >= 85:
            print("   👍 GOOD: System performing well with minor reconciliation needs")
        elif overall_match_rate >= 70:
            print("   ⚠️ MODERATE: Investigation required for unmatched entries")
        else:
            print("   🚨 CRITICAL: Immediate attention needed - significant reconciliation issues")
        
        print("="*80)


def main():
    """Main execution function."""
    # Initialize the reconciliation system
    system = CommissionReconciliationSystem()
    
    # Run full reconciliation process
    system.run_full_reconciliation()


if __name__ == "__main__":
    main()