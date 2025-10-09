#!/usr/bin/env python3
"""
Comprehensive debugging script to troubleshoot the $0.00 subscriber total issue.
"""

import sys
import os
sys.path.append('src')

from src.commission_processor import CommissionProcessor
from src.llm_extraction_service import LLMExtractionService
import logging

def setup_debug_logging():
    """Set up detailed logging for debugging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Enable debug logging for key components
    logging.getLogger('LLMExtractionService').setLevel(logging.DEBUG)
    logging.getLogger('ReconciliationEngine').setLevel(logging.DEBUG)
    logging.getLogger('CommissionProcessor').setLevel(logging.DEBUG)

def debug_extraction_only():
    """Debug just the extraction process for each carrier."""
    print("🔍 DEBUGGING EXTRACTION PROCESS")
    print("=" * 60)
    
    service = LLMExtractionService()
    
    # Test each carrier's PDF
    test_files = {
        'humana': 'docs/Humana_commission_statement_jul.pdf',
        'hne': 'docs/HNE comm.pdf', 
        'hc': 'docs/HC_COMMISSION_1462-001_R.pdf'
    }
    
    for carrier, pdf_path in test_files.items():
        print(f"\n📄 TESTING {carrier.upper()} EXTRACTION")
        print("-" * 40)
        
        if not os.path.exists(pdf_path):
            print(f"❌ PDF not found: {pdf_path}")
            continue
            
        try:
            # Read PDF text and extract entries
            import fitz
            doc = fitz.open(pdf_path)
            pdf_text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pdf_text += page.get_text()
            
            # This will trigger our debug logging
            entries = service.extract_commission_entries(pdf_text, carrier)
            
            print(f"✅ EXTRACTED {len(entries)} entries for {carrier}")
            for i, entry in enumerate(entries, 1):
                policy = entry.get('policy_number', 'MISSING')
                amount = entry.get('commission_amount', entry.get('amount', 'MISSING'))
                member = entry.get('member_name', 'MISSING')
                print(f"   {i}. Policy: {policy} | Amount: ${amount} | Member: {member}")
                
                # Check for issues
                if policy == 'MISSING':
                    print(f"      ❌ ISSUE: Missing policy number")
                if str(policy).startswith('INVALID_NAME_'):
                    print(f"      ❌ ISSUE: Policy number is a name")
                if amount == 'MISSING' or amount == 0:
                    print(f"      ❌ ISSUE: Missing or zero commission amount")
                    
        except Exception as e:
            print(f"❌ ERROR extracting from {carrier}: {e}")

def debug_reconciliation():
    """Debug the full reconciliation process."""
    print("\n🔍 DEBUGGING FULL RECONCILIATION PROCESS")  
    print("=" * 60)
    
    try:
        processor = CommissionProcessor()
        
        # Process with debug logging enabled
        results = processor.process_all_commission_statements()
        
        print(f"\n📊 RECONCILIATION RESULTS:")
        for carrier, data in results.items():
            print(f"\n{carrier.upper()}:")
            if 'extracted_entries' in data:
                print(f"   Extracted Entries: {len(data['extracted_entries'])}")
                for entry in data['extracted_entries']:
                    policy = entry.get('policy_number', 'MISSING')
                    amount = entry.get('commission_amount', entry.get('amount', 'MISSING'))
                    print(f"      Policy: {policy} | Amount: ${amount}")
            
            if 'reconciliation_results' in data:
                reconciliation = data['reconciliation_results']
                print(f"   Reconciliation Results:")
                print(f"      Total Entries: {reconciliation.get('total_entries', 0)}")
                print(f"      Matched: {reconciliation.get('matched_entries', 0)}")
                print(f"      Unmatched: {reconciliation.get('unmatched_entries', 0)}")
                
                # Check for $0.00 issues
                if 'details' in reconciliation:
                    for detail in reconciliation['details']:
                        actual = detail.get('actual_commission', 0)
                        expected = detail.get('expected_commission', 0)
                        if actual == 0 and expected > 0:
                            policy = detail.get('policy_number', 'UNKNOWN')
                            member = detail.get('member_name', 'UNKNOWN')
                            print(f"      ❌ $0.00 ISSUE: Policy {policy} ({member}) - Actual: $0.00, Expected: ${expected}")
                    
    except Exception as e:
        print(f"❌ ERROR in reconciliation: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the comprehensive debugging."""
    print("🚨 TROUBLESHOOTING $0.00 SUBSCRIBER TOTAL ISSUE")
    print("=" * 60)
    
    # Set up debug logging
    setup_debug_logging()
    
    # Step 1: Debug extraction only
    debug_extraction_only()
    
    # Step 2: Debug full reconciliation
    debug_reconciliation()
    
    print("\n📋 TROUBLESHOOTING SUMMARY:")
    print("1. Check the extraction debug logs above")
    print("2. Look for 'MISSING' policy numbers or amounts")
    print("3. Check for 'INVALID_NAME_' policy numbers") 
    print("4. Verify that extracted amounts are not 0")
    print("5. Compare extracted policy numbers with enrollment data")
    print("6. Look for reconciliation matching issues")

if __name__ == "__main__":
    main()