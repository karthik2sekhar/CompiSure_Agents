#!/usr/bin/env python3
"""
Extract and analyze the actual PDF report to see the $0.00 issue.
"""

import sys
import os
sys.path.append('src')

def read_pdf_report():
    """Read the actual PDF report to see the $0.00 issue."""
    print("🔍 READING ACTUAL PDF REPORT")
    print("=" * 60)
    
    pdf_path = 'reports/commission_reconciliation_summary_20251007_143848.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    try:
        import fitz
        doc = fitz.open(pdf_path)
        
        print(f"📄 PDF has {len(doc)} pages")
        
        full_text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            full_text += page_text
            
            print(f"\n📄 PAGE {page_num + 1} CONTENT:")
            print("-" * 40)
            print(page_text)
            print("-" * 40)
        
        # Look for the $0.00 issues specifically
        print(f"\n🔍 SEARCHING FOR $0.00 ISSUES:")
        lines = full_text.split('\n')
        
        for i, line in enumerate(lines):
            if '$0.00' in line and ('below expected' in line or 'Subscriber total' in line):
                print(f"   ❌ FOUND $0.00 ISSUE on line {i}: {line.strip()}")
                
                # Show context around the issue
                start = max(0, i-2)
                end = min(len(lines), i+3)
                print(f"      Context:")
                for j in range(start, end):
                    marker = " >>> " if j == i else "     "
                    print(f"{marker}{lines[j].strip()}")
                print()
        
        doc.close()
        
    except Exception as e:
        print(f"❌ ERROR reading PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    read_pdf_report()