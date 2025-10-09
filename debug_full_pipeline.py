#!/usr/bin/env python3
"""
Debug script to test the full commission processing pipeline and see where the $0.00 issue occurs.
"""

import sys
import os
sys.path.append('src')

from src.commission_processor import CommissionProcessor
import logging

def setup_debug_logging():
    """Set up detailed logging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_commission_processing():
    """Test the full commission processing pipeline."""
    print("🔍 DEBUGGING FULL COMMISSION PROCESSING PIPELINE")
    print("=" * 70)
    
    setup_debug_logging()
    
    try:
        processor = CommissionProcessor()
        
        print("\n📄 Available PDF files:")
        import glob
        pdf_files = glob.glob("docs/*.pdf")
        for pdf_file in pdf_files:
            print(f"   {pdf_file}")
        
        print("\n🔍 Processing commission statements...")
        docs_dir = "docs"
        results = processor.process_all_statements(docs_dir)
        
        print(f"\n📊 PROCESSING RESULTS:")
        for carrier, data in results.items():
            print(f"\n{carrier.upper()}:")
            
            # Check extracted entries (stored in 'commissions' by CommissionProcessor)
            if 'commissions' in data:
                extracted = data['commissions']
                print(f"   ✅ Extracted Entries: {len(extracted)}")
                for i, entry in enumerate(extracted[:3], 1):  # Show first 3
                    policy = entry.get('policy_number', 'MISSING')
                    amount = entry.get('commission_amount', entry.get('amount', 'MISSING'))
                    member = entry.get('member_name', 'MISSING')
                    print(f"      {i}. Policy: {policy} | Amount: ${amount} | Member: {member}")
                    
                    # Check for $0.00 issue
                    if float(amount) == 0.0:
                        print(f"      ⚠️  ZERO AMOUNT DETECTED for Policy {policy}")
                    else:
                        print(f"      ✅ NON-ZERO AMOUNT: ${amount}")
            else:
                print("   ❌ No commissions found")
            
            # Check reconciliation results
            if 'reconciliation_results' in data:
                reconciliation = data['reconciliation_results']
                print(f"   Reconciliation Results:")
                
                if 'subscriber_variances' in reconciliation:
                    variances = reconciliation['subscriber_variances']
                    print(f"      Subscriber Variances: {len(variances)}")
                    
                    for variance in variances[:3]:  # Show first 3
                        policy = variance.get('policy_id', 'UNKNOWN')
                        subscriber = variance.get('subscriber_name', 'UNKNOWN')
                        actual = variance.get('actual_commission', 0)
                        expected = variance.get('expected_commission', 0)
                        
                        if actual == 0.0 and expected > 0.0:
                            print(f"      ❌ ZERO ISSUE: Policy {policy} ({subscriber}) - Actual: $0.00, Expected: ${expected}")
                        else:
                            print(f"      ✅ OK: Policy {policy} ({subscriber}) - Actual: ${actual}, Expected: ${expected}")
                else:
                    print("      ❌ No subscriber_variances found")
            else:
                print("   ❌ No reconciliation_results found")
        
        print(f"\n🎯 SUMMARY:")
        print("If you see '❌ ZERO ISSUE' above, that's causing the $0.00 subscriber totals")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_commission_processing()