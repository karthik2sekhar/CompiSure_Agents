#!/usr/bin/env python3
"""
Test the fixed HNE extraction with real PDF data.
"""

import sys
import os
sys.path.append('src')

from src.llm_extraction_service import LLMExtractionService
from src.reconciliation_engine import ReconciliationEngine
import logging

def setup_debug_logging():
    """Set up detailed logging for debugging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_fixed_hne_extraction():
    """Test the fixed HNE extraction with real PDF data."""
    print("🔧 TESTING FIXED HNE EXTRACTION")
    print("=" * 60)
    
    setup_debug_logging()
    
    service = LLMExtractionService()
    
    # Read the actual HNE PDF
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
        
        print(f"📄 PDF loaded: {len(pdf_text)} characters")
        
        # Test the extraction
        print("\n🔍 RUNNING EXTRACTION...")
        entries = service.extract_commission_entries(pdf_text, 'hne')
        
        print(f"\n📊 EXTRACTION RESULTS: {len(entries)} entries found")
        for i, entry in enumerate(entries, 1):
            policy = entry.get('policy_number', 'MISSING')
            amount = entry.get('commission_amount', entry.get('amount', 'MISSING'))
            member = entry.get('member_name', 'MISSING')
            print(f"   {i}. Policy: {policy} | Amount: ${amount} | Member: {member}")
        
        # Test reconciliation
        print("\n🔍 TESTING RECONCILIATION...")
        engine = ReconciliationEngine()
        
        commission_data = {
            'hne': {
                'carrier': 'hne',
                'commissions': entries
            }
        }
        
        variance_results = engine._calculate_variance(commission_data['hne'])
        
        print(f"\n📊 RECONCILIATION RESULTS:")
        print(f"   Total Actual: ${variance_results.get('actual_commissions', 0)}")
        print(f"   Total Expected: ${variance_results.get('expected_commissions', 0)}")
        print(f"   Subscriber Variances: {len(variance_results.get('subscriber_variances', []))}")
        
        # Check for $0.00 issues
        zero_issues = 0
        for variance in variance_results.get('subscriber_variances', []):
            actual = variance.get('actual_commission', 0)
            expected = variance.get('expected_commission', 0)
            policy = variance.get('policy_id', 'UNKNOWN')
            member = variance.get('subscriber_name', 'UNKNOWN')
            
            if actual == 0.0 and expected > 0.0:
                print(f"   ❌ $0.00 ISSUE: Policy {policy} ({member}) - Actual: $0.00, Expected: ${expected}")
                zero_issues += 1
            else:
                print(f"   ✅ OK: Policy {policy} ({member}) - Actual: ${actual}, Expected: ${expected}")
        
        print(f"\n🎯 FINAL RESULT:")
        if zero_issues == 0:
            print("   ✅ SUCCESS: No more $0.00 subscriber total issues!")
            print("   ✅ All commission entries are properly extracted and reconciled")
        else:
            print(f"   ❌ STILL HAVE ISSUES: {zero_issues} policies showing $0.00")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_hne_extraction()