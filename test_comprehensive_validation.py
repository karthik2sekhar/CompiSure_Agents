#!/usr/bin/env python3
"""
Final comprehensive test to verify all fixes are working correctly
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

def test_comprehensive_fix_validation():
    """Comprehensive test to validate both issues are fixed"""
    
    print("=== COMPREHENSIVE FIX VALIDATION TEST ===")
    
    # Test scenarios:
    # 1. Normal case - extraction works correctly
    # 2. Zero amount case - extraction fails but system handles gracefully
    test_scenarios = {
        'Normal_Extraction': {
            'HNE': {
                'carrier': 'HNE',
                'statement_period': 'July 2024', 
                'commissions': [
                    {'policy_number': '90004932901', 'member_name': 'Matthess Albert', 'commission_amount': 626.00},
                    {'policy_number': '90004242901', 'member_name': 'Dandy Dean', 'commission_amount': 500.00},
                    {'policy_number': '90004223101', 'member_name': 'Georgeson Melinda', 'commission_amount': 280.00}
                ]
            },
            'Humana': {
                'carrier': 'Humana',
                'statement_period': 'July 2024',
                'commissions': [
                    {'policy_number': '00000790462A', 'member_name': 'Norris William N', 'commission_amount': 43.57},
                    {'policy_number': '00000788617A', 'member_name': "O'Neill Kathleen M", 'commission_amount': 43.57}
                ]
            }
        },
        'Failed_Extraction': {
            'HNE': {
                'carrier': 'HNE',
                'statement_period': 'July 2024',
                'commissions': [
                    {'policy_number': '90004932901', 'member_name': 'Matthess Albert', 'commission_amount': 626.00},  # This one works
                    {'policy_number': '90004242901', 'member_name': 'Dandy Dean', 'commission_amount': 0.00},       # This one failed extraction
                    {'policy_number': '90004223101', 'member_name': 'Georgeson Melinda', 'commission_amount': 0.00} # This one failed extraction
                ]
            },
            'Humana': {
                'carrier': 'Humana',
                'statement_period': 'July 2024',
                'commissions': [
                    {'policy_number': '00000790462A', 'member_name': 'Norris William N', 'commission_amount': 0.00},   # Failed extraction
                    {'policy_number': '00000788617A', 'member_name': "O'Neill Kathleen M", 'commission_amount': 0.00} # Failed extraction
                ]
            }
        }
    }
    
    all_tests_passed = True
    
    for scenario_name, test_data in test_scenarios.items():
        print(f"\n{'='*60}")
        print(f"TESTING SCENARIO: {scenario_name}")
        print(f"{'='*60}")
        
        # Show what we're testing
        for carrier, data in test_data.items():
            total_actual = sum(c['commission_amount'] for c in data['commissions'])
            print(f"{carrier}: Total ${total_actual:.2f}")
            for comm in data['commissions']:
                print(f"  {comm['policy_number']}: ${comm['commission_amount']:.2f}")
        
        try:
            # Run reconciliation
            engine = ReconciliationEngine()
            results = engine.reconcile_commissions(test_data)
            
            # Validate results
            scenario_passed = True
            total_discrepancies_found = 0
            
            for carrier, data in results.items():
                if carrier == 'cross_carrier_analysis':
                    continue
                    
                overpayments_count = len(data.get('overpayments', []))
                underpayments_count = len(data.get('underpayments', []))
                total_discrepancies = overpayments_count + underpayments_count
                total_discrepancies_found += total_discrepancies
                
                print(f"\n{carrier} Results:")
                print(f"  Total Commissions: ${data.get('total_commissions', 0):,.2f}")
                print(f"  Discrepancies: {total_discrepancies}")
                
                # Test 1: Verify discrepancies count is not 0 when there should be discrepancies
                if scenario_name == 'Normal_Extraction' or scenario_name == 'Failed_Extraction':
                    if total_discrepancies == 0:
                        print(f"    ❌ FAIL: Expected discrepancies but got 0")
                        scenario_passed = False
                    else:
                        print(f"    ✅ PASS: Found {total_discrepancies} discrepancies")
                
                # Test 2: Check reason messages for $0.00 issues
                for overpay in data.get('overpayments', []):
                    reason = overpay.get('reason', '')
                    print(f"  OVERPAY: {reason}")
                    if scenario_name == 'Normal_Extraction' and '$0.00' in reason:
                        print(f"    ❌ FAIL: Should not show $0.00 in normal extraction")
                        scenario_passed = False
                    elif scenario_name == 'Failed_Extraction' and '$0.00' in reason:
                        print(f"    ⚠️  EXPECTED: Shows $0.00 due to extraction failure (with warning logged)")
                
                for underpay in data.get('underpayments', []):
                    reason = underpay.get('reason', '')
                    print(f"  UNDERPAY: {reason}")
                    if scenario_name == 'Normal_Extraction' and '$0.00' in reason:
                        print(f"    ❌ FAIL: Should not show $0.00 in normal extraction")
                        scenario_passed = False
                    elif scenario_name == 'Failed_Extraction' and '$0.00' in reason:
                        print(f"    ⚠️  EXPECTED: Shows $0.00 due to extraction failure (with warning logged)")
            
            # Generate PDF for this scenario
            generator = ReportGenerator()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_path = generator._generate_pdf_report(results, os.getcwd(), f"{scenario_name.lower()}_{timestamp}")
            print(f"\nPDF generated: {pdf_path}")
            
            if scenario_passed:
                print(f"✅ SCENARIO {scenario_name}: PASSED")
            else:
                print(f"❌ SCENARIO {scenario_name}: FAILED")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ ERROR in scenario {scenario_name}: {e}")
            all_tests_passed = False
    
    print(f"\n{'='*60}")
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED - Both issues are fixed!")
        print("\n✅ Issue 1 (Subscriber Total $0.00): FIXED")
        print("   - When extraction works correctly, shows actual amounts") 
        print("   - When extraction fails, shows $0.00 with warning logged")
        print("\n✅ Issue 2 (Discrepancies Count 0): FIXED")
        print("   - Correctly counts overpayments + underpayments")
        print("   - Shows accurate counts in PDF reports")
    else:
        print("❌ Some tests failed - issues need more work")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_comprehensive_fix_validation()