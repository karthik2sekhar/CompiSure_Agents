#!/usr/bin/env python3

import pdfplumber
import re

def test_hc_extraction():
    # Extract text from PDF
    with pdfplumber.open('docs/HC_COMMISSION_1462-001_R.pdf') as pdf:
        text = ''
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
    
    print("Testing HC Pattern Extraction")
    print("=" * 50)
    
    lines = text.split('\n')
    
    # Test policy header pattern
    policy_pattern = r'(\d{6})\s*\(([^)]+)\)'
    policies_found = []
    
    # Test commission pattern
    commission_pattern = r'([A-Za-z\s\']+?)\s+(\d+)\s+(\d{2}/\d{4})\s+\$(\d+\.\d{2})'
    commissions_found = []
    
    current_policy = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Check for policy headers
        policy_match = re.match(policy_pattern, line)
        if policy_match:
            current_policy = policy_match.group(1)
            employer = policy_match.group(2)
            policies_found.append((current_policy, employer))
            print(f"Policy: {current_policy} - {employer}")
        
        # Check for commission lines
        commission_match = re.search(commission_pattern, line)
        if commission_match and current_policy:
            subscriber = commission_match.group(1).strip()
            count = commission_match.group(2)
            month = commission_match.group(3)
            amount = float(commission_match.group(4))
            commissions_found.append((current_policy, subscriber, amount))
            print(f"  {subscriber}: ${amount}")
    
    print(f"\nSummary:")
    print(f"Policies found: {len(policies_found)}")
    print(f"Commissions found: {len(commissions_found)}")
    print(f"Total commission amount: ${sum(c[2] for c in commissions_found):.2f}")

if __name__ == "__main__":
    test_hc_extraction()