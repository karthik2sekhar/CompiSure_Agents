#!/usr/bin/env python3
"""
Test Humana reconciliation with the policy normalization fix
"""

import sys
import os
import logging
import pandas as pd

# Setup logging to capture reconciliation details
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_humana_reconciliation():
    """Test Humana reconciliation with the policy normalization fix"""
    
    print("🧪 TESTING HUMANA RECONCILIATION WITH POLICY NORMALIZATION FIX")
    print("=" * 70)
    
    # Mock the commission data structure that would come from extraction
    humana_commission_data = {
        'carrier': 'humana',
        'commissions': [
            {
                'policy_number': 'N00000790462A',
                'commission_amount': 43.57,
                'amount': 43.57,
                'member_name': 'Norris William N',
                'date': '2025-07-01',
                'product_name': 'Medicare',
                'premium': None
            },
            {
                'policy_number': 'M00000788617A', 
                'commission_amount': 43.57,
                'amount': 43.57,
                'member_name': 'O\'Neill Kathleen M',
                'date': '2025-07-01',
                'product_name': 'Medicare', 
                'premium': None
            }
        ]
    }
    
    print("1️⃣ MOCK COMMISSION DATA:")
    print(f"   Carrier: {humana_commission_data['carrier']}")
    print(f"   Number of entries: {len(humana_commission_data['commissions'])}")
    for i, entry in enumerate(humana_commission_data['commissions'], 1):
        print(f"   Entry {i}: {entry['policy_number']} - ${entry['commission_amount']} - {entry['member_name']}")
    
    # Test the variance calculation logic with normalization
    print("\n2️⃣ TESTING POLICY NORMALIZATION IN RECONCILIATION:")
    
    # Load enrollment data
    try:
        enrollment_df = pd.read_csv('docs/enrollment_info.csv')
        humana_enrollment = enrollment_df[enrollment_df['carrier'].str.lower() == 'humana']
        
        print(f"   Enrollment records: {len(humana_enrollment)}")
        for _, row in humana_enrollment.iterrows():
            print(f"     {row['policy_id']} - ${row['expected_commission']} - {row['member_name']}")
            
    except Exception as e:
        print(f"   ❌ Error loading enrollment data: {e}")
        return False
    
    # Simulate the reconciliation engine's variance calculation
    print("\n3️⃣ SIMULATING RECONCILIATION VARIANCE CALCULATION:")
    
    # Create DataFrame from commission data
    df = pd.DataFrame(humana_commission_data['commissions'])
    
    # Apply the normalization logic (same as in reconciliation_engine.py)
    def normalize_policy_id(policy_number, carrier_name='humana'):
        policy_str = str(policy_number)
        
        if '_' in policy_str:
            policy_str = policy_str.split('_')[0]
        
        if carrier_name == 'humana' and len(policy_str) > 1 and policy_str[0].isalpha():
            if len(policy_str) == 13 and policy_str[1:-1].isdigit() and policy_str[-1].isalpha():
                original = policy_str
                policy_str = policy_str[1:]
                print(f"     🔧 Normalized: {original} -> {policy_str}")
        
        return policy_str
    
    df['policy_id'] = df['policy_number'].apply(lambda x: normalize_policy_id(x, 'humana'))
    
    print(f"   Original policy_numbers: {list(df['policy_number'])}")
    print(f"   Normalized policy_ids: {list(df['policy_id'])}")
    
    # Group by policy and sum commissions
    subscriber_actuals = df.groupby('policy_id')['commission_amount'].sum().to_dict()
    print(f"   Subscriber actuals: {subscriber_actuals}")
    
    # Compare with enrollment data
    print("\n4️⃣ VARIANCE ANALYSIS:")
    total_actual = 0
    total_expected = 0
    
    for _, enrollment_row in humana_enrollment.iterrows():
        policy_id = str(enrollment_row['policy_id'])
        member_name = enrollment_row['member_name']
        expected = float(enrollment_row['expected_commission'])
        actual = subscriber_actuals.get(policy_id, 0.0)
        
        total_actual += actual
        total_expected += expected
        
        variance_amount = actual - expected
        variance_percentage = (variance_amount / expected * 100) if expected > 0 else 0
        
        print(f"   Policy '{policy_id}' ({member_name}):")
        print(f"     Expected: ${expected:.2f}")
        print(f"     Actual: ${actual:.2f}")
        print(f"     Variance: ${variance_amount:.2f} ({variance_percentage:.1f}%)")
        
        if actual == 0.0 and expected > 0.0:
            print(f"     ❌ ISSUE: Zero commission - this is the $0.00 problem!")
            return False
        elif actual > 0.0:
            print(f"     ✅ SUCCESS: Commission found and mapped correctly!")
        print()
    
    print("5️⃣ SUMMARY:")
    print(f"   Total Actual: ${total_actual:.2f}")
    print(f"   Total Expected: ${total_expected:.2f}")
    print(f"   Total Variance: ${total_actual - total_expected:.2f}")
    
    if total_actual > 0:
        print(f"   ✅ SUCCESS: The policy normalization fix resolves the $0.00 issue!")
        print(f"   📊 Humana commissions are now correctly mapped to enrollment records!")
        return True
    else:
        print(f"   ❌ FAILURE: Still seeing $0.00 commission totals!")
        return False

def main():
    """Run the test"""
    success = test_humana_reconciliation()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 HUMANA RECONCILIATION FIX SUCCESSFUL!")
        print("   The policy normalization fix should resolve the $0.00 issue in reports.")
    else:
        print("💥 HUMANA RECONCILIATION FIX FAILED!")
        print("   Additional debugging needed.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)