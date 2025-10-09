#!/usr/bin/env python3
"""
PHI Scrubber Service - Anonymizes PHI data before LLM processing while preserving structure for accuracy.

This service removes Protected Health Information (PHI) from commission statements before sending
to external AI services, then restores the original PHI to the extracted results.
"""

import re
import logging
from typing import Dict, Tuple, List
from datetime import datetime
import hashlib


class PHIScrubber:
    """Service to anonymize PHI data before external LLM processing while maintaining extraction accuracy."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def scrub_commission_statement(self, pdf_text: str) -> Tuple[str, Dict[str, str]]:
        """
        Remove PHI from commission statement text and return mapping for restoration.
        
        Args:
            pdf_text: Original text containing PHI
            
        Returns:
            Tuple of (scrubbed_text, phi_mapping)
        """
        scrubbed_text = pdf_text
        phi_mapping = {}
        
        # 1. Scrub member/subscriber names (highest priority PHI)
        scrubbed_text, name_mapping = self._scrub_names(scrubbed_text)
        phi_mapping.update(name_mapping)
        
        # 2. Scrub policy numbers (replace with consistent placeholders)
        scrubbed_text, policy_mapping = self._scrub_policy_numbers(scrubbed_text)
        phi_mapping.update(policy_mapping)
        
        # 3. Scrub employer/company names
        scrubbed_text, company_mapping = self._scrub_company_names(scrubbed_text)
        phi_mapping.update(company_mapping)
        
        # 4. Scrub addresses if present
        scrubbed_text, address_mapping = self._scrub_addresses(scrubbed_text)
        phi_mapping.update(address_mapping)
        
        # 5. Scrub phone numbers
        scrubbed_text, phone_mapping = self._scrub_phone_numbers(scrubbed_text)
        phi_mapping.update(phone_mapping)
        
        # 6. Scrub email addresses
        scrubbed_text, email_mapping = self._scrub_email_addresses(scrubbed_text)
        phi_mapping.update(email_mapping)
        
        # Log scrubbing statistics
        self.logger.info(f"PHI Scrubbing completed: {len(phi_mapping)} items anonymized")
        self.logger.debug(f"Scrubbed: Names={len(name_mapping)}, Policies={len(policy_mapping)}, "
                         f"Companies={len(company_mapping)}, Addresses={len(address_mapping)}, "
                         f"Phones={len(phone_mapping)}, Emails={len(email_mapping)}")
        
        return scrubbed_text, phi_mapping
    
    def _scrub_names(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Replace person names with generic placeholders while preserving structure."""
        name_mapping = {}
        scrubbed_text = text
        
        # Enhanced name patterns to catch various formats
        name_patterns = [
            # Standard: FirstName LastName
            r'\b([A-Z][a-z]{1,15})\s+([A-Z][a-z]{1,20})\b',
            # With middle initial: FirstName M. LastName
            r'\b([A-Z][a-z]{1,15})\s+([A-Z]\.?\s+)?([A-Z][a-z]{1,20})\b',
            # With apostrophe: John O'Connor, Mary D'Amico
            r'\b([A-Z][a-z]{1,15})\s+([A-Z]\'[A-Z]?[a-z]{1,20})\b',
            # Hyphenated names: Mary-Jane Smith
            r'\b([A-Z][a-z]{1,15}(?:-[A-Z][a-z]{1,15})?)\s+([A-Z][a-z]{1,20})\b',
            # LastName, FirstName format
            r'\b([A-Z][a-z]{1,20}),\s+([A-Z][a-z]{1,15})\b',
        ]
        
        name_counter = 1
        processed_names = set()  # Avoid duplicate processing
        
        for pattern in name_patterns:
            matches = list(re.finditer(pattern, scrubbed_text))
            for match in matches:
                full_name = match.group(0).strip()
                
                # Skip if already processed or if it's a false positive
                if full_name in processed_names or not self._is_likely_person_name(full_name):
                    continue
                
                placeholder = f"MEMBER_{name_counter:03d}"
                name_mapping[placeholder] = full_name
                scrubbed_text = scrubbed_text.replace(full_name, placeholder)
                processed_names.add(full_name)
                name_counter += 1
        
        return scrubbed_text, name_mapping
    
    def _scrub_policy_numbers(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Replace policy numbers with consistent placeholders."""
        policy_mapping = {}
        scrubbed_text = text
        
        # Different policy number patterns for various carriers
        policy_patterns = [
            # Humana format: 11 digits + letter (with or without prefix)
            (r'\b[A-Z]?(\d{11}[A-Z])\b', 'HUMANA'),
            # HC format: 6 digits
            (r'\b(\d{6})\b', 'HC'),
            # HNE format: 11 digits (member ID)
            (r'\b(\d{11})\b', 'HNE'),
            # General policy formats
            (r'\b([A-Z]{2,4}\d{6,10})\b', 'GENERAL'),
            # Alphanumeric policies
            (r'\b([A-Z]\d{4,10}[A-Z]?)\b', 'ALPHA'),
        ]
        
        policy_counter = 1
        processed_policies = set()
        
        for pattern, carrier_hint in policy_patterns:
            matches = list(re.finditer(pattern, scrubbed_text))
            for match in matches:
                policy_num = match.group(1) if match.lastindex >= 1 else match.group(0)
                
                # Skip if already processed or too generic
                if policy_num in processed_policies or not self._is_likely_policy_number(policy_num):
                    continue
                
                placeholder = f"POLICY_{policy_counter:03d}"
                policy_mapping[placeholder] = policy_num
                
                # Replace the full match (including any prefix)
                full_match = match.group(0)
                scrubbed_text = scrubbed_text.replace(full_match, placeholder)
                processed_policies.add(policy_num)
                policy_counter += 1
        
        return scrubbed_text, policy_mapping
    
    def _scrub_company_names(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Replace company/employer names with placeholders."""
        company_mapping = {}
        scrubbed_text = text
        
        # Company name patterns
        company_patterns = [
            # HC format: "(Company Name)"
            r'\(([^)]{3,50})\)',
            # General business names with common suffixes
            r'\b([A-Z][A-Za-z\s&,.\'-]{3,40}(?:LLC|Inc|Corp|Company|Co\.|Ltd|LP|LLP)\.?)\b',
            # Business names with "The"
            r'\b(The\s+[A-Z][A-Za-z\s&,.\'-]{3,30}(?:LLC|Inc|Corp|Company|Co\.|Ltd)?\.?)\b',
        ]
        
        company_counter = 1
        processed_companies = set()
        
        for pattern in company_patterns:
            matches = list(re.finditer(pattern, scrubbed_text, re.IGNORECASE))
            for match in matches:
                company_name = match.group(1).strip()
                
                # Skip if already processed or not likely a company
                if company_name in processed_companies or not self._is_likely_company_name(company_name):
                    continue
                
                placeholder = f"EMPLOYER_{company_counter:03d}"
                company_mapping[placeholder] = company_name
                
                # For parenthetical format, preserve the parentheses
                if match.group(0).startswith('('):
                    scrubbed_text = scrubbed_text.replace(f"({company_name})", f"({placeholder})")
                else:
                    scrubbed_text = scrubbed_text.replace(company_name, placeholder)
                
                processed_companies.add(company_name)
                company_counter += 1
        
        return scrubbed_text, company_mapping
    
    def _scrub_addresses(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Replace addresses with placeholders."""
        address_mapping = {}
        scrubbed_text = text
        
        # Address patterns
        address_patterns = [
            # Street addresses: "123 Main Street"
            r'\b(\d+\s+[A-Z][A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\.?)\b',
            # City, State ZIP: "Boston, MA 02101"
            r'\b([A-Z][A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}(?:-\d{4})?)\b',
            # PO Boxes
            r'\b(P\.?O\.?\s+Box\s+\d+)\b',
        ]
        
        address_counter = 1
        
        for pattern in address_patterns:
            matches = list(re.finditer(pattern, scrubbed_text, re.IGNORECASE))
            for match in matches:
                address = match.group(1).strip()
                placeholder = f"ADDRESS_{address_counter:03d}"
                address_mapping[placeholder] = address
                scrubbed_text = scrubbed_text.replace(address, placeholder)
                address_counter += 1
        
        return scrubbed_text, address_mapping
    
    def _scrub_phone_numbers(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Replace phone numbers with placeholders."""
        phone_mapping = {}
        scrubbed_text = text
        
        # Phone number patterns
        phone_patterns = [
            r'\b(\d{3}-\d{3}-\d{4})\b',        # 123-456-7890
            r'\b(\(\d{3}\)\s*\d{3}-\d{4})\b',  # (123) 456-7890
            r'\b(\d{10})\b',                   # 1234567890 (only if looks like phone)
            r'\b(1-\d{3}-\d{3}-\d{4})\b',     # 1-123-456-7890
        ]
        
        phone_counter = 1
        
        for pattern in phone_patterns:
            matches = list(re.finditer(pattern, scrubbed_text))
            for match in matches:
                phone = match.group(1)
                
                # For 10-digit numbers, verify they look like phone numbers
                if len(phone) == 10 and not phone.startswith(('0', '1')):
                    placeholder = f"PHONE_{phone_counter:03d}"
                    phone_mapping[placeholder] = phone
                    scrubbed_text = scrubbed_text.replace(phone, placeholder)
                    phone_counter += 1
                elif len(phone) != 10:  # Other formats are likely phones
                    placeholder = f"PHONE_{phone_counter:03d}"
                    phone_mapping[placeholder] = phone
                    scrubbed_text = scrubbed_text.replace(phone, placeholder)
                    phone_counter += 1
        
        return scrubbed_text, phone_mapping
    
    def _scrub_email_addresses(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Replace email addresses with placeholders."""
        email_mapping = {}
        scrubbed_text = text
        
        # Email pattern
        email_pattern = r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b'
        
        email_counter = 1
        matches = re.finditer(email_pattern, scrubbed_text)
        
        for match in matches:
            email = match.group(1)
            placeholder = f"EMAIL_{email_counter:03d}"
            email_mapping[placeholder] = email
            scrubbed_text = scrubbed_text.replace(email, placeholder)
            email_counter += 1
        
        return scrubbed_text, email_mapping
    
    def _is_likely_person_name(self, text: str) -> bool:
        """Check if text is likely a person's name."""
        # Skip common false positives
        false_positives = {
            'Sub Total', 'Employer Total', 'Grand Total', 'Health Connector',
            'Blue Cross', 'Member ID', 'Policy Number', 'Commission Amount',
            'July August', 'May June', 'Total Paid', 'Coverage Period',
            'Dear Beth', 'Beth Evans', 'Eye Street', 'Page Number'
        }
        
        if text in false_positives:
            return False
        
        # Must be at least 2 words
        words = text.split()
        if len(words) < 2:
            return False
        
        # Each word should be reasonable length for names
        for word in words:
            if len(word) < 2 or len(word) > 20:
                return False
        
        # Skip if it looks like a business name
        business_indicators = ['LLC', 'Inc', 'Corp', 'Company', 'Co.', 'Ltd', 'LP', 'LLP']
        if any(indicator in text for indicator in business_indicators):
            return False
        
        return True
    
    def _is_likely_policy_number(self, text: str) -> bool:
        """Check if text is likely a policy number."""
        # Skip if too short or too long
        if len(text) < 4 or len(text) > 15:
            return False
        
        # Skip common false positives (dates, amounts, etc.)
        if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):  # Dates
            return False
        if re.match(r'^\d{4}$', text):  # Years
            return False
        if text in ['07/2025', '2025', '1225']:  # Common date fragments
            return False
        
        return True
    
    def _is_likely_company_name(self, text: str) -> bool:
        """Check if text is likely a company name."""
        # Skip obvious non-companies
        if re.match(r'^\d+$', text.strip()):  # Pure numbers
            return False
        if len(text.strip()) < 3:  # Too short
            return False
        if text.strip() in ['Page', 'Total', 'Amount', 'Commission']:  # Common false positives
            return False
        
        return True
    
    def restore_phi_to_extracted_data(self, extracted_data: List[Dict], phi_mapping: Dict[str, str]) -> List[Dict]:
        """Restore original PHI to the extracted commission data."""
        restored_data = []
        
        for entry in extracted_data:
            restored_entry = entry.copy()
            
            # Restore each field that might contain placeholders
            for field_name, field_value in entry.items():
                if isinstance(field_value, str):
                    restored_value = field_value
                    
                    # Replace any placeholders with original PHI
                    for placeholder, original_value in phi_mapping.items():
                        if placeholder in restored_value:
                            restored_value = restored_value.replace(placeholder, original_value)
                    
                    restored_entry[field_name] = restored_value
            
            restored_data.append(restored_entry)
        
        return restored_data
    
    def get_scrubbing_statistics(self, phi_mapping: Dict[str, str]) -> Dict:
        """Get statistics about the scrubbing operation for monitoring."""
        stats = {
            'total_items_scrubbed': len(phi_mapping),
            'members_scrubbed': len([k for k in phi_mapping.keys() if k.startswith('MEMBER_')]),
            'policies_scrubbed': len([k for k in phi_mapping.keys() if k.startswith('POLICY_')]),
            'employers_scrubbed': len([k for k in phi_mapping.keys() if k.startswith('EMPLOYER_')]),
            'addresses_scrubbed': len([k for k in phi_mapping.keys() if k.startswith('ADDRESS_')]),
            'phones_scrubbed': len([k for k in phi_mapping.keys() if k.startswith('PHONE_')]),
            'emails_scrubbed': len([k for k in phi_mapping.keys() if k.startswith('EMAIL_')]),
            'scrubbing_timestamp': datetime.now().isoformat()
        }
        
        return stats