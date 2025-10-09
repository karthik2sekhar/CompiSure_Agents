#!/usr/bin/env python3
"""
Test the improved HNE pattern.
"""

import re
import sys
import os
sys.path.append('src')

def test_improved_pattern():
    """Test the improved HNE pattern."""
    print("🔧 TESTING IMPROVED HNE PATTERN")
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
        
        # Test the new pattern
        hne_pattern = r'(H\d{4})\s*\n\s*(\w+)\s*\n\s*(\d{11})\s*\n.*?\n.*?\n\s*(\w+)\s*\n\s*(\w+)\s*\n.*?(?:NEW|RENEW)\s*\n.*?\n([\d.]+)'
        
        print(f"📄 PDF text length: {len(pdf_text)}")
        print(f"\n🔍 Testing pattern: {hne_pattern}")
        
        matches = re.findall(hne_pattern, pdf_text, re.DOTALL)
        print(f"   Found {len(matches)} matches")
        
        for i, match in enumerate(matches, 1):
            h_code, txn_id, member_id, last_name, first_name, amount = match
            print(f"      Match {i}: H-code={h_code}, TxnID={txn_id}, MemberID={member_id}, Name={first_name} {last_name}, Amount=${amount}")
        
        # If that doesn't work, try a simpler approach
        if len(matches) == 0:
            print("\n🔍 Trying simpler line-by-line parsing...")
            
            lines = pdf_text.split('\n')
            entries = []
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Look for H-code lines
                if re.match(r'H\d{4}', line):
                    h_code = line
                    
                    # Look for the next few lines to get the data
                    if i + 7 < len(lines):
                        txn_id = lines[i + 1].strip()
                        member_id = lines[i + 2].strip()
                        
                        # Skip some lines to get to names
                        last_name = None
                        first_name = None
                        
                        # Look for names in the next several lines
                        for j in range(i + 3, min(i + 15, len(lines))):
                            if re.match(r'^[A-Z][a-z]+$', lines[j].strip()):
                                if not last_name:
                                    last_name = lines[j].strip()
                                elif not first_name:
                                    first_name = lines[j].strip()
                                    break
                        
                        # Look for commission amount (last number before next H-code or end)
                        amount = None
                        for j in range(i + 1, min(i + 20, len(lines))):
                            if j < len(lines) - 1 and re.match(r'H\d{4}', lines[j + 1].strip()):
                                # Next H-code found, look backwards for amount
                                for k in range(j, i, -1):
                                    if re.match(r'^\d+\.\d+$', lines[k].strip()):
                                        amount = lines[k].strip()
                                        break
                                break
                            elif j == len(lines) - 1 or 'Sub Total' in lines[j]:
                                # End reached, look backwards for amount
                                for k in range(j, i, -1):
                                    if re.match(r'^\d+\.\d+$', lines[k].strip()):
                                        amount = lines[k].strip()
                                        break
                                break
                        
                        if member_id and re.match(r'\d{11}', member_id) and amount:
                            entry = {
                                'h_code': h_code,
                                'txn_id': txn_id,
                                'member_id': member_id,
                                'last_name': last_name,
                                'first_name': first_name,
                                'amount': amount
                            }
                            entries.append(entry)
                            print(f"   Entry: {h_code} | {member_id} | {first_name} {last_name} | ${amount}")
                
                i += 1
            
            print(f"\n🎯 Simple parsing found {len(entries)} entries")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_pattern()