#!/usr/bin/env python3
"""
Debug the HNE regex pattern to see why it's not matching.
"""

import re
import sys
import os
sys.path.append('src')

def debug_hne_pattern():
    """Debug the HNE pattern matching."""
    print("🔍 DEBUGGING HNE PATTERN MATCHING")
    print("=" * 60)
    
    # Read the actual PDF text
    pdf_path = 'docs/HNE comm.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    try:
        import fitz
        doc = fitz.open(pdf_path)
        pdf_text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pdf_text += page.get_text()
        doc.close()
        
        print(f"📄 PDF text length: {len(pdf_text)}")
        print(f"\n📄 PDF text (first 500 chars):")
        print(repr(pdf_text[:500]))
        
        # Test different regex patterns
        patterns_to_test = [
            (r'(H\d{4})\s+(\w+)\s+(\d{11})\s+(\w+)\s+(\w+)\s+\w+\s+[\d.]+\s+([\d.]+)', "Original pattern"),
            (r'(H\d{4})\s+(\S+)\s+(\d{11})\s+(\S+)\s+(\S+).*?([\d.]+)', "Simplified pattern"), 
            (r'H\d{4}.*?(\d{11}).*?([\d.]+)', "Very simple pattern"),
            (r'(H2737|H8578).*?(\d{11}).*?([\d.]+)', "Specific H-codes"),
        ]
        
        for pattern, description in patterns_to_test:
            print(f"\n🔍 Testing {description}: {pattern}")
            matches = re.findall(pattern, pdf_text, re.DOTALL)
            print(f"   Found {len(matches)} matches")
            
            for i, match in enumerate(matches[:3], 1):  # Show first 3 matches
                print(f"      Match {i}: {match}")
        
        # Let's also manually look for the data we expect
        print(f"\n🔍 Manual search for expected data:")
        expected_data = [
            'H2737', 'H8578', 
            '90004932901', '90004242901', '90004223101',
            'Matthess', 'Albert', 'Dandy', 'Dean', 'Georgeson', 'Melinda',
            '626.00', '286.92'
        ]
        
        for item in expected_data:
            if item in pdf_text:
                print(f"   ✅ Found: '{item}'")
                # Show context
                start = pdf_text.find(item)
                context = pdf_text[max(0, start-50):start+100]
                print(f"      Context: ...{context}...")
            else:
                print(f"   ❌ Missing: '{item}'")
                
        # Show lines that contain our target data
        print(f"\n🔍 Lines containing commission data:")
        lines = pdf_text.split('\n')
        for i, line in enumerate(lines):
            if any(target in line for target in ['H2737', 'H8578', '90004932901', '90004242901', '90004223101']):
                print(f"   Line {i}: {repr(line)}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_hne_pattern()