#!/usr/bin/env python3
"""
Debug script to test HC commission extraction specifically.
"""

import sys
import os
sys.path.append('src')

from src.llm_extraction_service import LLMExtractionService
import logging

def setup_debug_logging():
    """Set up detailed logging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_hc_extraction():
    """Test HC commission extraction specifically."""
    print("🔍 DEBUGGING HC COMMISSION EXTRACTION")
    print("=" * 50)
    
    setup_debug_logging()
    
    try:
        # Initialize LLM service
        service = LLMExtractionService()
        
        # Test HC extraction
        hc_pdf = "docs/HC_COMMISSION_1462-001_R.pdf"
        if os.path.exists(hc_pdf):
            print(f"\n📄 Testing HC extraction on: {hc_pdf}")
            
            # Extract text first
            text = ""
            with open(hc_pdf, 'rb') as file:
                import pdfplumber
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
            
            # Extract commission data
            results = service.extract_commission_entries(text, "hc")
            
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
                
                # Try to understand why
                print("\n🔍 Debugging extraction process...")
                
                # Check if HC extractor is available
                if hasattr(service, 'hc_extractor') and service.hc_extractor:
                    print("   ✅ HC pattern extractor is available")
                    
                    # Try direct pattern extraction
                    print("\n   Testing direct pattern extraction...")
                    try:
                        import pdfplumber
                        
                        # Extract text using pdfplumber
                        text = ""
                        with pdfplumber.open(hc_pdf) as pdf:
                            for page in pdf.pages:
                                text += page.extract_text() or ""
                        
                        print(f"   PDF text length: {len(text)} characters")
                        print(f"   PDF text preview: {text[:200]}...")
                        
                        # Test pattern extraction directly
                        pattern_results = service.hc_extractor.extract_commissions(text)
                        print(f"   Pattern extraction results: {len(pattern_results)} entries")
                        
                        if pattern_results:
                            for i, entry in enumerate(pattern_results[:2], 1):
                                print(f"      Pattern {i}: {entry}")
                        
                    except Exception as e:
                        print(f"   ❌ Pattern extraction error: {e}")
                        import traceback
                        traceback.print_exc()
                        
                else:
                    print("   ❌ HC pattern extractor is NOT available")
        else:
            print(f"❌ HC PDF not found: {hc_pdf}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hc_extraction()