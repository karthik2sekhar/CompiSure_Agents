#!/usr/bin/env python3
"""
Compare HC pattern extractor with the known working test_hc_pattern.py approach.
"""

import PyPDF2
import re
from src.pattern_extractors.hc_extractor import HCPatternExtractor

def compare_extraction_methods():
    """Compare our new extractor with the working pattern from test_hc_pattern.py."""
    
    # Extract text from HC PDF
    with open('docs/HC_COMMISSION_1462-001_R.pdf', 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    
    print("=== METHOD 1: New HC Pattern Extractor ===")
    extractor = HCPatternExtractor()
    new_entries = extractor.extract_commission_entries(full_text)
    new_total = sum(entry.get('amount', 0) for entry in new_entries)
    print(f"Entries: {len(new_entries)}, Total: ${new_total:.2f}")
    
    print("\n=== METHOD 2: Original Working Pattern (from test_hc_pattern.py) ===")
    # Original working pattern from test_hc_pattern.py
    policies = {}
    lines = full_text.split('\n')
    
    current_policy = None
    current_employer = None
    
    for line in lines:
        line = line.strip()
        
        # Check for policy line
        policy_match = re.match(r'^(\d{6})\s*\(([^)]+)\)', line)
        if policy_match:
            current_policy = policy_match.group(1)
            current_employer = policy_match.group(2)
            if current_policy not in policies:
                policies[current_policy] = {'employer': current_employer, 'members': []}
            continue
        
        # Check for member commission line
        if current_policy and '$' in line:
            # Look for pattern: Name [numbers] Month/Year $Amount
            commission_match = re.search(r'^([A-Za-z\s\'.-]+?)\s+\d+\s+\d{2}/\d{4}\s+\$(\d+(?:\.\d{2})?)', line)
            if commission_match:
                member_name = commission_match.group(1).strip()
                amount_str = commission_match.group(2)
                
                # Skip headers
                if any(word in member_name.lower() for word in ['subscriber', 'enrolled', 'month', 'commission']):
                    continue
                
                try:
                    amount = float(amount_str)
                    policies[current_policy]['members'].append({
                        'name': member_name,
                        'amount': amount
                    })
                except ValueError:
                    continue
    
    # Count original entries
    original_count = 0
    original_total = 0
    for policy_num, policy_data in policies.items():
        for member in policy_data['members']:
            original_count += 1
            original_total += member['amount']
    
    print(f"Entries: {original_count}, Total: ${original_total:.2f}")
    
    print(f"\n=== COMPARISON ===")
    print(f"New extractor: {len(new_entries)} entries, ${new_total:.2f}")
    print(f"Original method: {original_count} entries, ${original_total:.2f}")
    print(f"Difference: {original_count - len(new_entries)} entries, ${original_total - new_total:.2f}")

if __name__ == "__main__":
    compare_extraction_methods()