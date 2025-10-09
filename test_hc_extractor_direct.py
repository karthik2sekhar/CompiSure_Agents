#!/usr/bin/env python3
"""
Test HC pattern extractor directly.
"""

import PyPDF2
from src.pattern_extractors.hc_extractor import HCPatternExtractor

def test_hc_extractor():
    """Test HC pattern extractor directly."""
    
    # Extract text from HC PDF
    with open('docs/HC_COMMISSION_1462-001_R.pdf', 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    
    # Test HC extractor
    extractor = HCPatternExtractor()
    entries = extractor.extract_commission_entries(full_text)
    
    total_amount = sum(entry.get('amount', 0) for entry in entries)
    
    print(f"HC Pattern Extractor Results:")
    print(f"Entries extracted: {len(entries)}")
    print(f"Total amount: ${total_amount:.2f}")
    
    if len(entries) >= 80 and total_amount >= 1000:
        print("✅ SUCCESS: HC pattern extractor works correctly!")
        return True
    else:
        print("⚠️ CONCERN: Pattern extractor may need adjustment")
        # Show first few entries for debugging
        for i, entry in enumerate(entries[:5]):
            print(f"  {i+1}: {entry}")
        return False

if __name__ == "__main__":
    test_hc_extractor()