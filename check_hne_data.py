#!/usr/bin/env python3
"""
Check HNE data for policy mapping issues
"""

import pandas as pd

def check_hne_data():
    """Check HNE enrollment and extraction data for mapping issues"""
    
    print("📊 HNE DATA ANALYSIS")
    print("=" * 40)
    
    # Check HNE enrollment data
    enrollment_df = pd.read_csv('docs/enrollment_info.csv')
    hne_enrollment = enrollment_df[enrollment_df['carrier'].str.lower() == 'hne']
    
    print("1️⃣ HNE ENROLLMENT DATA:")
    print(f"   Number of records: {len(hne_enrollment)}")
    for _, row in hne_enrollment.iterrows():
        print(f"     policy_id: {row['policy_id']}")
        print(f"     member_name: {row['member_name']}")
        print(f"     expected_commission: {row['expected_commission']}")
        print()
    
    print("2️⃣ HNE EXTRACTION DATA (from previous debug):")
    extracted_data = [
        {'policy': '90004932901', 'amount': 199.84, 'member': 'Matthess Albert'},
        {'policy': '90004242901', 'amount': 0.0, 'member': 'Dandy Dean'},
        {'policy': '90004223101', 'amount': 199.84, 'member': 'Georgeson Melinda'}
    ]
    
    for entry in extracted_data:
        print(f"     Policy: {entry['policy']} - Amount: ${entry['amount']} - Member: {entry['member']}")
    print()
    
    print("3️⃣ POLICY MAPPING ANALYSIS:")
    enrollment_policies = [str(p) for p in hne_enrollment['policy_id']]
    extracted_policies = [entry['policy'] for entry in extracted_data]
    
    print(f"   Enrollment policy IDs: {enrollment_policies}")
    print(f"   Extracted policy numbers: {extracted_policies}")
    print()
    
    print("4️⃣ MATCH CHECK:")
    all_match = True
    for extracted in extracted_policies:
        if extracted in enrollment_policies:
            print(f"   ✅ MATCH: '{extracted}' found in enrollment")
        else:
            print(f"   ❌ NO MATCH: '{extracted}' not found in enrollment")
            all_match = False
    
    if all_match:
        print("\n✅ HNE POLICY MAPPING: All policies match correctly!")
        print("   HNE does not have the same issue as Humana.")
    else:
        print("\n❌ HNE POLICY MAPPING: Some policies don't match!")
        print("   HNE may have similar issues to Humana.")
    
    print("\n5️⃣ HNE ZERO COMMISSION ANALYSIS:")
    print("   From the report, HNE shows 'Subscriber total $0.00' issues.")
    print("   But our extraction shows non-zero amounts for most policies.")
    print("   The issue might be different from Humana's policy ID mismatch.")
    
    # Check if the zero amount is legitimate
    zero_policies = [entry for entry in extracted_data if entry['amount'] == 0.0]
    if zero_policies:
        print(f"\n   🔍 ZERO COMMISSION POLICIES:")
        for entry in zero_policies:
            # Find corresponding enrollment
            enrollment_match = hne_enrollment[hne_enrollment['policy_id'] == entry['policy']]
            if not enrollment_match.empty:
                expected = enrollment_match.iloc[0]['expected_commission']
                print(f"     Policy {entry['policy']} ({entry['member']}):")
                print(f"       Extracted: ${entry['amount']}")
                print(f"       Expected: ${expected}")
                if expected > 0:
                    print(f"       ❌ ISSUE: Should have commission but extracted $0.00")
                else:
                    print(f"       ✅ OK: Zero commission is expected")
    
    return all_match

if __name__ == "__main__":
    check_hne_data()