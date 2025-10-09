#!/usr/bin/env python3
"""
Debug script to test reconciliation with simulated commission data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from src.reconciliation_engine import ReconciliationEngine

# Set up logging to see debug messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')

def test_reconciliation_with_simulated_data():
    """Test reconciliation with simulated data to debug the $0 issue"""
    
    print("Testing reconciliation with simulated commission data...")
    
    # Create simulated commission data based on your example
    simulated_data = {
        'HNE': {
            'carrier': 'HNE',
            'statement_period': 'July 2024',
            'commissions': [
                {
                    'policy_number': '90004932901',
                    'member_name': 'Matthess Albert',
                    'commission_amount': 626.00  # You mentioned this was the actual amount
                },
                {
                    'policy_number': '90004242901', 
                    'member_name': 'Dandy Dean',
                    'commission_amount': 500.00  # Simulated amount
                },
                {
                    'policy_number': '90004223101',
                    'member_name': 'Georgeson Melinda', 
                    'commission_amount': 200.00  # Simulated amount
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
                    'commission_amount': 47.14  # Split the total $87.14
                },
                {
                    'policy_number': '00000788617A',
                    'member_name': "O'Neill Kathleen M",
                    'commission_amount': 40.00  # Split the total $87.14
                }
            ]
        }
    }
    
    try:
        engine = ReconciliationEngine()
        
        # Test HNE reconciliation
        print("\n=== TESTING HNE RECONCILIATION ===")
        hne_results = engine.reconcile_commissions({'HNE': simulated_data['HNE']})
        
        print("HNE Results:")
        for carrier, data in hne_results.items():
            if carrier != 'cross_carrier_analysis':
                print(f"  {carrier}:")
                print(f"    Overpayments: {len(data.get('overpayments', []))}")
                print(f"    Underpayments: {len(data.get('underpayments', []))}")
                for underpay in data.get('underpayments', []):
                    print(f"      Policy {underpay.get('policy_number')}: {underpay.get('reason')}")
        
        # Test Humana reconciliation
        print("\n=== TESTING HUMANA RECONCILIATION ===")
        humana_results = engine.reconcile_commissions({'Humana': simulated_data['Humana']})
        
        print("Humana Results:")
        for carrier, data in humana_results.items():
            if carrier != 'cross_carrier_analysis':
                print(f"  {carrier}:")
                print(f"    Overpayments: {len(data.get('overpayments', []))}")
                print(f"    Underpayments: {len(data.get('underpayments', []))}")
                for underpay in data.get('underpayments', []):
                    print(f"      Policy {underpay.get('policy_number')}: {underpay.get('reason')}")
        
    except Exception as e:
        print(f"Error during reconciliation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reconciliation_with_simulated_data()