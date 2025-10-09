#!/usr/bin/env python3
"""
Simple debug script to identify Humana policy mapping issue
"""

import sys
import os
import pandas as pd

# Change to src directory for imports
os.chdir('src')
sys.path.insert(0, '.')

from commission_processor import CommissionProcessor
import logging

logging.basicConfig(level=logging.INFO)

print("🔍 DEBUGGING HUMANA POLICY MAPPING ISSUE")
print("=" * 50)

# Process commission statements
processor = CommissionProcessor()
commission_data = processor.process_all_statements('../docs')

print("\n1️⃣ HUMANA EXTRACTION RESULTS:")
if 'humana' in commission_data:
    humana_data = commission_data['humana']
    commissions = humana_data.get('commissions', [])
    print(f"   Number of entries: {len(commissions)}")
    for i, entry in enumerate(commissions):
        print(f"   Entry {i+1}:")
        policy_num = entry.get('policy_number', 'N/A')
        commission_amt = entry.get('commission_amount', 'N/A')
        member_name = entry.get('member_name', 'N/A')
        print(f"     policy_number: '{policy_num}'")
        print(f"     commission_amount: {commission_amt}")
        print(f"     member_name: '{member_name}'")
        print()
else:
    print("   ❌ No Humana data found")
    sys.exit(1)

print("\n2️⃣ ENROLLMENT DATA FOR HUMANA:")
enrollment_df = pd.read_csv('../docs/enrollment_info.csv')
humana_enrollment = enrollment_df[enrollment_df['carrier'].str.lower() == 'humana']
print(f"   Number of enrollment records: {len(humana_enrollment)}")
for _, row in humana_enrollment.iterrows():
    print(f"     policy_id: '{row['policy_id']}'")
    print(f"     member_name: '{row['member_name']}'")
    print(f"     expected_commission: {row['expected_commission']}")
    print()

print("\n3️⃣ MAPPING ANALYSIS:")
extracted_policies = [entry.get('policy_number', '') for entry in commissions]
enrollment_policies = list(humana_enrollment['policy_id'])

print(f"   Extracted policy numbers: {extracted_policies}")
print(f"   Enrollment policy IDs: {enrollment_policies}")

print("\n4️⃣ EXACT MATCH CHECK:")
for extracted in extracted_policies:
    if extracted in enrollment_policies:
        print(f"   ✅ MATCH: '{extracted}' found in enrollment")
    else:
        print(f"   ❌ NO MATCH: '{extracted}' not found in enrollment")

print("\n5️⃣ RECONCILIATION SIMULATION:")
# Simulate what reconciliation engine does
subscriber_actuals = {}
for entry in commissions:
    policy_number = entry.get('policy_number', '')
    # This is what reconciliation does - split on underscore
    policy_id = str(policy_number).split('_')[0] if '_' in str(policy_number) else str(policy_number)
    commission_amount = float(entry.get('commission_amount', 0))
    
    if policy_id in subscriber_actuals:
        subscriber_actuals[policy_id] += commission_amount
    else:
        subscriber_actuals[policy_id] = commission_amount

print(f"   Grouped subscriber actuals: {subscriber_actuals}")

print("\n6️⃣ FINAL MAPPING:")
for _, enrollment_row in humana_enrollment.iterrows():
    policy_id = str(enrollment_row['policy_id'])
    member_name = enrollment_row['member_name']
    expected = float(enrollment_row['expected_commission'])
    actual = subscriber_actuals.get(policy_id, 0.0)
    
    print(f"   Policy '{policy_id}' ({member_name}):")
    print(f"     Expected: ${expected:.2f}")
    print(f"     Actual: ${actual:.2f}")
    if actual == 0.0 and expected > 0.0:
        print(f"     ❌ ISSUE: No actual commission found!")
    else:
        print(f"     ✅ OK: Commission mapped correctly")
    print()