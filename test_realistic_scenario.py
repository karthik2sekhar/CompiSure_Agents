#!/usr/bin/env python3
"""
Test with realistic commission amounts to verify both fixes
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

def test_realistic_scenario():
    """Test with realistic commission amounts that should show correct totals and discrepancies"""
    
    print("=== TESTING REALISTIC SCENARIO ===")
    
    # Create test data with realistic amounts - some overpayments, some underpayments
    test_commission_data = {
        'HNE': {
            'carrier': 'HNE',
            'statement_period': 'July 2024',
            'commissions': [
                {
                    'policy_number': '90004932901',
                    'member_name': 'Matthess Albert',
                    'commission_amount': 626.00  # Expected $300 -> Overpayment of $326
                },
                {
                    'policy_number': '90004242901', 
                    'member_name': 'Dandy Dean',
                    'commission_amount': 500.00  # Expected $650 -> Underpayment of $150
                },
                {
                    'policy_number': '90004223101',
                    'member_name': 'Georgeson Melinda', 
                    'commission_amount': 250.00  # Expected $280 -> Underpayment of $30
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
                    'commission_amount': 43.57  # Expected $100 -> Underpayment of $56.43
                },
                {
                    'policy_number': '00000788617A',
                    'member_name': "O'Neill Kathleen M",
                    'commission_amount': 43.57  # Expected $55 -> Underpayment of $11.43
                }
            ]
        }
    }
    
    print("Commission data being processed:")
    for carrier, data in test_commission_data.items():
        total_actual = sum(c['commission_amount'] for c in data['commissions'])
        print(f"\n{carrier}: Total ${total_actual:.2f}")
        for comm in data['commissions']:
            print(f"  {comm['policy_number']}: ${comm['commission_amount']:.2f}")
    
    try:
        # Run reconciliation
        engine = ReconciliationEngine()
        results = engine.reconcile_commissions(test_commission_data)
        
        print("\n=== RECONCILIATION RESULTS ===")
        
        total_discrepancies_found = 0
        
        # Analyze results
        for carrier, data in results.items():
            if carrier == 'cross_carrier_analysis':
                continue
                
            overpayments_count = len(data.get('overpayments', []))
            underpayments_count = len(data.get('underpayments', []))
            total_discrepancies = overpayments_count + underpayments_count
            total_discrepancies_found += total_discrepancies
            
            print(f"\n{carrier}:")
            print(f"  Total Commissions: ${data.get('total_commissions', 0):,.2f}")
            print(f"  Variance Amount: ${data.get('variance_amount', 0):,.2f}")
            print(f"  Overpayments: {overpayments_count}")
            print(f"  Underpayments: {underpayments_count}")
            print(f"  Total Discrepancies: {total_discrepancies}")
            
            # Show the reason messages - should NOT have $0.00 now
            for overpay in data.get('overpayments', []):
                reason = overpay.get('reason', '')
                print(f"  OVERPAY: {reason}")
                if '$0.00' in reason:
                    print(f"    ❌ ERROR: Still showing $0.00!")
                else:
                    print(f"    ✅ FIXED: Showing correct amounts")
            
            for underpay in data.get('underpayments', []):
                reason = underpay.get('reason', '')
                print(f"  UNDERPAY: {reason}")
                if '$0.00' in reason:
                    print(f"    ❌ ERROR: Still showing $0.00!")
                else:
                    print(f"    ✅ FIXED: Showing correct amounts")
        
        print(f"\nTotal discrepancies across all carriers: {total_discrepancies_found}")
        
        # Generate PDF to test discrepancies count display
        print("\n=== GENERATING REALISTIC TEST PDF ===")
        generator = ReportGenerator()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        pdf_path = generator._generate_pdf_report(results, os.getcwd(), f"realistic_test_{timestamp}")
        print(f"✅ Realistic test PDF generated: {pdf_path}")
        print("Please review the PDF to confirm:")
        print("1. Discrepancies count shows correct numbers (not 0)")
        print("2. Subscriber total amounts show actual values (not $0.00)")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during realistic test: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_realistic_scenario()