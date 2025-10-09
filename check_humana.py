#!/usr/bin/env python3
"""
Quick test to see Humana PDF structure for pattern extraction.
"""

import pdfplumber

def check_humana_pdf():
    """Check what the Humana PDF looks like."""
    print("🔍 CHECKING HUMANA PDF STRUCTURE")
    print("=" * 40)
    
    humana_pdf = "docs/Humana_commission_statement_jul.pdf"
    
    try:
        with pdfplumber.open(humana_pdf) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        print(f"📄 PDF text length: {len(text)} characters")
        print(f"📄 PDF text preview (first 800 chars):")
        print(text[:800])
        print("...")
        
        # Look for patterns
        import re
        
        # Check for dollar amounts with different formats
        dollar_formats = [
            r'\$[\d,]+\.?\d*',      # $1,234.56
            r'[\d,]+\.\d{2}',       # 1,234.56
            r'\$[\d.]+',            # $1234.56
        ]
        
        for i, pattern in enumerate(dollar_formats, 1):
            matches = re.findall(pattern, text)
            print(f"   Dollar format {i}: {len(matches)} matches")
            if matches:
                print(f"      First few: {matches[:5]}")
        
        # Check for potential policy numbers
        policy_patterns = [
            r'\b\d{8,12}\b',        # 8-12 digit numbers
            r'\b[A-Z]{2,}\d+\b',    # Letters followed by numbers
        ]
        
        for i, pattern in enumerate(policy_patterns, 1):
            matches = re.findall(pattern, text)
            print(f"   Policy pattern {i}: {len(matches)} matches")
            if matches:
                print(f"      First few: {matches[:5]}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_humana_pdf()