#!/usr/bin/env python3
"""
Debug script to check Humana policy mapping issue
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Fix import issues
import importlib.util
spec = importlib.util.spec_from_file_location("commission_processor", "src/commission_processor.py")
commission_processor = importlib.util.module_from_spec(spec)
sys.modules["commission_processor"] = commission_processor

# Import related modules first
spec_llm = importlib.util.spec_from_file_location("llm_extraction_service", "src/llm_extraction_service.py")
llm_service = importlib.util.module_from_spec(spec_llm)
sys.modules["llm_extraction_service"] = llm_service
spec_llm.loader.exec_module(llm_service)

spec.loader.exec_module(commission_processor)
CommissionProcessor = commission_processor.CommissionProcessor
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("🔍 DEBUGGING HUMANA POLICY MAPPING ISSUE")
    print("=" * 50)
    
    # Process commission statements
    processor = CommissionProcessor()
    commission_data = processor.process_all_statements('docs')
    
    print("\n1️⃣ HUMANA EXTRACTION RESULTS:")
    if 'humana' in commission_data:
        humana_data = commission_data['humana']
        commissions = humana_data.get('commissions', [])
        print(f"   Number of entries: {len(commissions)}")
        for i, entry in enumerate(commissions):
            print(f"   Entry {i+1}:")
            print(f"     policy_number: '{entry.get('policy_number', 'N/A')}'")
            print(f"     commission_amount: {entry.get('commission_amount', 'N/A')}")
            print(f"     member_name: '{entry.get('member_name', 'N/A')}'")
            print()
    else:
        print("   ❌ No Humana data found")
        return
    
    print("\n2️⃣ ENROLLMENT DATA FOR HUMANA:")
    enrollment_df = pd.read_csv('docs/enrollment_info.csv')
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
            # Check for partial matches
            for enrollment_id in enrollment_policies:
                if str(extracted) in str(enrollment_id) or str(enrollment_id) in str(extracted):
                    print(f"      🔍 PARTIAL MATCH: '{extracted}' ~ '{enrollment_id}'")
    
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

if __name__ == "__main__":
    main()