#!/usr/bin/env python3
"""
Debug script to trace commission data flow and identify $0.00 issue
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from src.reconciliation_engine import ReconciliationEngine
from src.report_generator import ReportGenerator
from datetime import datetime

# Set up comprehensive logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')

def test_data_flow_with_zero_amounts():
    """Test to understand why we get $0.00 subscriber totals"""
    
    print("=== TESTING DATA FLOW FOR $0.00 ISSUE ===")
    
    # Create test data that mimics the real issue - some policies have extracted amounts, others don't
    test_commission_data = {
        'HNE': {
            'carrier': 'HNE',
            'statement_period': 'July 2024',
            'commissions': [
                {
                    'policy_number': '90004932901',
                    'member_name': 'Matthess Albert',
                    'commission_amount': 626.00  # This one has an amount
                },
                {
                    'policy_number': '90004242901', 
                    'member_name': 'Dandy Dean',
                    'commission_amount': 0.00  # This one shows $0.00 - extraction failed
                },
                {
                    'policy_number': '90004223101',
                    'member_name': 'Georgeson Melinda', 
                    'commission_amount': 0.00  # This one shows $0.00 - extraction failed
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
                    'commission_amount': 0.00  # This one shows $0.00 - extraction failed
                },
                {
                    'policy_number': '00000788617A',
                    'member_name': "O'Neill Kathleen M",
                    'commission_amount': 0.00  # This one shows $0.00 - extraction failed
                }
            ]
        }
    }
    
    print("Commission data being processed:")
    for carrier, data in test_commission_data.items():
        print(f"\n{carrier}:")
        for comm in data['commissions']:
            print(f"  {comm['policy_number']}: ${comm['commission_amount']}")
    
    try:
        # Run reconciliation with debug logging
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
            print(f"  Overpayments: {overpayments_count}")
            print(f"  Underpayments: {underpayments_count}")
            print(f"  Total Discrepancies: {total_discrepancies}")
            
            # Show the actual reason messages to see the $0.00 issue
            for overpay in data.get('overpayments', []):
                print(f"  OVERPAY: {overpay.get('reason')}")
            
            for underpay in data.get('underpayments', []):
                print(f"  UNDERPAY: {underpay.get('reason')}")
        
        print(f"\nTotal discrepancies across all carriers: {total_discrepancies_found}")
        
        # Generate PDF to test discrepancies count display
        print("\n=== GENERATING TEST PDF ===")
        generator = ReportGenerator()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        pdf_path = generator._generate_pdf_report(results, os.getcwd(), f"debug_flow_{timestamp}")
        print(f"Debug PDF generated: {pdf_path}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_data_flow_with_zero_amounts()