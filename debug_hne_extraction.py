#!/usr/bin/env python3
"""
Debug script to test HNE commission extraction specifically.
"""

import sys
import os
sys.path.append('src')

from src.llm_extraction_service import LLMExtractionService
import pdfplumber
import logging

def setup_debug_logging():
    """Set up detailed logging."""
    logging.basicConfig(
        level=logging.INFO,  # Less verbose than DEBUG
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_hne_extraction():
    """Test HNE commission extraction specifically."""
    print("🔍 DEBUGGING HNE COMMISSION EXTRACTION")
    print("=" * 50)
    
    setup_debug_logging()
    
    try:
        # Initialize LLM service
        service = LLMExtractionService()
        
        # Test HNE extraction
        hne_pdf = "docs/HNE comm.pdf"
        if os.path.exists(hne_pdf):
            print(f"\n📄 Testing HNE extraction on: {hne_pdf}")
            
            # Extract text first
            text = ""
            with pdfplumber.open(hne_pdf) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += page_text
            
            print(f"\n📄 PDF text length: {len(text)} characters")
            print(f"📄 PDF text preview (first 500 chars):")
            print(text[:500])
            print("...")
            
            # Look for commission patterns in the text
            print(f"\n🔍 Searching for commission patterns:")
            import re
            
            # Check for dollar amounts
            dollar_matches = re.findall(r'\$[\d,]+\.?\d*', text)
            print(f"   Dollar amounts found: {len(dollar_matches)}")
            if dollar_matches:
                print(f"   First few: {dollar_matches[:5]}")
            
            # Check for policy numbers
            policy_matches = re.findall(r'\b\d{8,12}\b', text)
            print(f"   Potential policy numbers: {len(policy_matches)}")
            if policy_matches:
                print(f"   First few: {policy_matches[:5]}")
            
            # Check for member names (capitalized words)
            name_matches = re.findall(r'\b[A-Z][a-z]+,?\s+[A-Z][a-z]+\b', text)
            print(f"   Potential member names: {len(name_matches)}")
            if name_matches:
                print(f"   First few: {name_matches[:5]}")
            
            # Extract commission data using the service
            print(f"\n🔄 Running HNE extraction...")
            results = service.extract_commission_entries(text, "hne")
            
            print(f"\n📊 EXTRACTION RESULTS:")
            print(f"   Number of entries: {len(results)}")
            
            if results:
                print("\n   First 3 entries:")
                for i, entry in enumerate(results[:3], 1):
                    policy = entry.get('policy_number', 'MISSING')
                    amount = entry.get('commission_amount', entry.get('amount', 'MISSING'))
                    member = entry.get('member_name', 'MISSING')
                    print(f"      {i}. Policy: {policy} | Amount: ${amount} | Member: {member}")
            else:
                print("   ❌ NO ENTRIES EXTRACTED")
                
                # Test the HNE pattern extraction directly
                print("\n🔍 Testing HNE pattern extraction directly...")
                try:
                    hne_results = service._extract_hne_commission_data(text)
                    print(f"   Direct HNE pattern results: {len(hne_results)} entries")
                    
                    if hne_results:
                        for i, entry in enumerate(hne_results[:2], 1):
                            print(f"      HNE Pattern {i}: {entry}")
                except Exception as e:
                    print(f"   ❌ Direct HNE pattern extraction error: {e}")
        else:
            print(f"❌ HNE PDF not found: {hne_pdf}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hne_extraction()