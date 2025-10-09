#!/usr/bin/env python3
"""
Debug script to examine what's actually in the HNE PDF and why extraction is missing policies.
"""

import sys
import os
sys.path.append('src')

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not available, using alternative approach")
    fitz = None

def analyze_hne_pdf():
    """Analyze the HNE PDF to see why extraction is missing policy 90004223101."""
    print("🔍 ANALYZING HNE PDF CONTENT")
    print("=" * 60)
    
    pdf_path = 'docs/HNE comm.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    try:
        if fitz:
            # Use PyMuPDF to extract text
            doc = fitz.open(pdf_path)
            pdf_text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pdf_text += page.get_text()
            doc.close()
        else:
            # Fallback to reading PDF as binary (limited)
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
                pdf_text = str(pdf_content)  # This won't work well but shows the attempt
        
        print(f"📄 PDF TEXT LENGTH: {len(pdf_text)} characters")
        print("\n🔍 SEARCHING FOR EXPECTED POLICY NUMBERS:")
        
        # Search for the specific policies we expect
        expected_policies = [
            '90004932901',  # Matthess Albert - should be found
            '90004242901',  # Dandy Dean - should be found  
            '90004223101'   # Georgeson Melinda - MISSING in extraction
        ]
        
        expected_members = [
            'Matthess Albert',
            'Dandy Dean', 
            'Georgeson Melinda'
        ]
        
        for policy in expected_policies:
            if policy in pdf_text:
                print(f"   ✅ FOUND: Policy {policy} is in the PDF")
                # Find context around this policy
                start = pdf_text.find(policy)
                context = pdf_text[max(0, start-100):start+200]
                print(f"      Context: ...{context}...")
            else:
                print(f"   ❌ MISSING: Policy {policy} is NOT in the PDF text")
        
        print("\n🔍 SEARCHING FOR EXPECTED MEMBER NAMES:")
        for member in expected_members:
            if member in pdf_text:
                print(f"   ✅ FOUND: Member '{member}' is in the PDF")
            else:
                print(f"   ❌ MISSING: Member '{member}' is NOT in the PDF text")
        
        print("\n🔍 SEARCHING FOR COMMISSION AMOUNTS:")
        # Look for the expected commission amounts
        expected_amounts = ['626.00', '650.00', '280.00']
        for amount in expected_amounts:
            if amount in pdf_text:
                print(f"   ✅ FOUND: Amount ${amount} is in the PDF")
            else:
                print(f"   ❌ MISSING: Amount ${amount} is NOT in the PDF text")
        
        print("\n🔍 PDF TEXT SAMPLE (first 1000 characters):")
        print("-" * 40)
        print(pdf_text[:1000])
        print("-" * 40)
        
        print("\n🔍 PATTERN ANALYSIS:")
        # Look for HNE-specific patterns
        hne_patterns = [
            'H2737', 'H8578',  # H-codes
            'Member ID', 'Contract ID', 'Transaction ID',
            'Commission', 'Premium'
        ]
        
        for pattern in hne_patterns:
            if pattern in pdf_text:
                print(f"   ✅ FOUND: Pattern '{pattern}' is in the PDF")
            else:
                print(f"   ❌ MISSING: Pattern '{pattern}' is NOT in the PDF text")
                
    except Exception as e:
        print(f"❌ ERROR analyzing PDF: {e}")
        import traceback
        traceback.print_exc()

def check_enrollment_data():
    """Check what the enrollment data expects vs what extraction finds."""
    print("\n🔍 CHECKING ENROLLMENT DATA")
    print("=" * 60)
    
    try:
        import pandas as pd
        
        # Try to load enrollment data
        enrollment_file = 'docs/enrollment_info.csv'
        if os.path.exists(enrollment_file):
            df = pd.read_csv(enrollment_file)
            
            # Filter for HNE
            hne_records = df[df['carrier'].str.lower() == 'hne']
            print(f"📊 HNE ENROLLMENT RECORDS: {len(hne_records)}")
            
            for _, row in hne_records.iterrows():
                policy = row.get('policy_id', 'MISSING')
                member = row.get('member_name', 'MISSING')
                expected = row.get('expected_commission', 0)
                print(f"   Policy: {policy} | Member: {member} | Expected: ${expected}")
                
        else:
            print(f"❌ Enrollment file not found: {enrollment_file}")
            
    except Exception as e:
        print(f"❌ ERROR checking enrollment data: {e}")

if __name__ == "__main__":
    analyze_hne_pdf()
    check_enrollment_data()