#!/usr/bin/env python3
"""
Test to verify the $0.00 subscriber total fix
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from src.reconciliation_engine import ReconciliationEngine
from src.report_generator import ReportGenerator
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')

def test_zero_dollar_fix():
    """Test the fix for $0.00 subscriber total issue"""
    
    print("Testing fix for $0.00 subscriber total issue...")
    
    # Create test data that would previously show $0.00 but now should show correct amounts
    test_commission_data = {
        'HNE': {
            'carrier': 'HNE',
            'statement_period': 'July 2024',
            'commissions': [
                {
                    'policy_number': '90004932901',
                    'member_name': 'Matthess Albert',
                    'commission_amount': 626.00  # Your actual amount
                },
                {
                    'policy_number': '90004242901', 
                    'member_name': 'Dandy Dean',
                    'commission_amount': 0.00  # This should show underpayment
                },
                {
                    'policy_number': '90004223101',
                    'member_name': 'Georgeson Melinda', 
                    'commission_amount': 0.00  # This should show underpayment
                }
            ]
        },
        'Humana': {
            'carrier': 'Humana',
            'statement_period': 'July 2024',
            'commissions': [
                {
                    'policy_number': '00000790462A',
                    'member_name': 'Norris William N',
                    'commission_amount': 43.57  # Split of $87.14 total
                },
                {
                    'policy_number': '00000788617A',
                    'member_name': "O'Neill Kathleen M",
                    'commission_amount': 43.57  # Split of $87.14 total
                }
            ]
        }
    }
    
    try:
        # Run reconciliation
        engine = ReconciliationEngine()
        results = engine.reconcile_commissions(test_commission_data)
        
        print("\n=== RECONCILIATION RESULTS ===")
        
        # Check that we're no longer getting $0.00 subscriber totals
        for carrier, data in results.items():
            if carrier == 'cross_carrier_analysis':
                continue
                
            print(f"\n{carrier} Analysis:")
            
            # Check overpayments
            if data.get('overpayments'):
                print("Overpayments:")
                for overpay in data['overpayments']:
                    reason = overpay.get('reason', '')
                    print(f"  Policy {overpay.get('policy_number')}: {reason}")
                    # Verify we're not getting $0.00 in the reason
                    if '$0.00' in reason:
                        print(f"  ❌ ERROR: Still showing $0.00 in reason: {reason}")
                    else:
                        print(f"  ✅ FIXED: Showing correct amount in reason")
            
            # Check underpayments
            if data.get('underpayments'):
                print("Underpayments:")
                for underpay in data['underpayments']:
                    reason = underpay.get('reason', '')
                    print(f"  Policy {underpay.get('policy_number')}: {reason}")
                    # Verify we're not getting $0.00 in the reason
                    if '$0.00' in reason:
                        print(f"  ❌ ERROR: Still showing $0.00 in reason: {reason}")
                    else:
                        print(f"  ✅ FIXED: Showing correct amount in reason")
        
        # Generate a test report to verify PDF shows correct amounts
        print("\n=== GENERATING TEST REPORT ===")
        generator = ReportGenerator()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        pdf_path = generator._generate_pdf_report(results, os.getcwd(), timestamp)
        print(f"✅ Test PDF generated: {pdf_path}")
        print("Please verify the PDF shows correct 'Subscriber total' amounts instead of $0.00")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_zero_dollar_fix()