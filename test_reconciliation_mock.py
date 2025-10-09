#!/usr/bin/env python3
"""
Simple test to debug the $0.00 issue using mock data - no API key needed.
"""

import sys
import os
sys.path.append('src')

from src.reconciliation_engine import ReconciliationEngine
import logging

def setup_debug_logging():
    """Set up detailed logging for debugging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_reconciliation_with_mock_data():
    """Test reconciliation with mock data to identify the $0.00 issue."""
    print("🔍 TESTING RECONCILIATION WITH MOCK DATA")
    print("=" * 60)
    
    setup_debug_logging()
    engine = ReconciliationEngine()
    
    # Create mock commission data that mimics the extraction output
    # This simulates what the LLM extraction should return
    mock_commission_data = {
        'humana': {
            'carrier': 'humana',
            'commissions': [
                {
                    'policy_number': '00000790462A',  # Correct policy number
                    'commission_amount': 43.57,
                    'member_name': 'Norris William',
                    'date': '2025-07-01'
                },
                {
                    'policy_number': '00000788617A',  # Correct policy number
                    'commission_amount': 43.57,
                    'member_name': 'Neill Kathleen',
                    'date': '2025-07-01'
                }
            ]
        },
        'hne': {
            'carrier': 'hne',
            'commissions': [
                {
                    'policy_number': '90004932901',  # Correct policy number
                    'commission_amount': 626.00,
                    'member_name': 'Matthess Albert',
                    'date': '2025-07-01'
                },
                {
                    'policy_number': '90004242901',  # Correct policy number
                    'commission_amount': 650.00,
                    'member_name': 'Dandy Dean',
                    'date': '2025-07-01'
                }
            ]
        }
    }
    
    print("📊 MOCK COMMISSION DATA:")
    for carrier, data in mock_commission_data.items():
        print(f"\n{carrier.upper()}:")
        for entry in data['commissions']:
            print(f"   Policy: {entry['policy_number']} | Amount: ${entry['commission_amount']} | Member: {entry['member_name']}")
    
    print("\n🔍 RUNNING RECONCILIATION...")
    
    # Test the variance analysis specifically
    for carrier, data in mock_commission_data.items():
        print(f"\n--- TESTING {carrier.upper()} ---")
        
        try:
            variance_results = engine._calculate_variance(data)
            
            print(f"Variance Results:")
            print(f"   Total Actual: ${variance_results.get('actual_commissions', 0)}")
            print(f"   Total Expected: ${variance_results.get('expected_commissions', 0)}")
            print(f"   Subscriber Variances: {len(variance_results.get('subscriber_variances', []))}")
            
            # Check for $0.00 issues
            for variance in variance_results.get('subscriber_variances', []):
                actual = variance.get('actual_commission', 0)
                expected = variance.get('expected_commission', 0)
                policy = variance.get('policy_id', 'UNKNOWN')
                member = variance.get('subscriber_name', 'UNKNOWN')
                
                if actual == 0.0 and expected > 0.0:
                    print(f"   ❌ FOUND $0.00 ISSUE: Policy {policy} ({member}) - Actual: $0.00, Expected: ${expected}")
                else:
                    print(f"   ✅ OK: Policy {policy} ({member}) - Actual: ${actual}, Expected: ${expected}")
                    
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_reconciliation_with_mock_data()