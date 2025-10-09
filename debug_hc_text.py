#!/usr/bin/env python3
"""
Debug the HC PDF text format.
"""

import PyPDF2

def debug_hc_text():
    """Debug HC PDF text extraction."""
    
    # Extract text from HC PDF
    with open('docs/HC_COMMISSION_1462-001_R.pdf', 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    
    # Print first 2000 characters to see the format
    print("First 2000 characters of HC PDF text:")
    print("=" * 50)
    print(full_text[:2000])
    print("=" * 50)
    
    # Look for patterns
    import re
    policy_matches = re.findall(r'Policy.*?\d+', full_text[:2000])
    print(f"Found {len(policy_matches)} policy patterns in first 2000 chars:")
    for match in policy_matches[:5]:
        print(f"  - {match}")
        
    # Look for dollar amounts
    dollar_matches = re.findall(r'\$\d+(?:\.\d{2})?', full_text[:2000])
    print(f"Found {len(dollar_matches)} dollar amounts in first 2000 chars:")
    for match in dollar_matches[:10]:
        print(f"  - {match}")

if __name__ == "__main__":
    debug_hc_text()