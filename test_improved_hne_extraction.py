#!/usr/bin/env python3
"""
Fix the HNE extraction to ensure all commission entries are found.
"""

import sys
import os
sys.path.append('src')

def test_improved_hne_extraction():
    """Test improved HNE extraction logic."""
    print("🔧 TESTING IMPROVED HNE EXTRACTION")
    print("=" * 60)
    
    # The actual HNE PDF text (based on our analysis)
    hne_pdf_text = """
Health New England - Sales Commission Statement
Contract ID  Txn ID       Member ID    Member      Member      Pay Type  Rate    Payout
                          (HISN/MBI)   LastName    FirstName             Months  Amt
H2737       9P87YX0QG32  90004932901  Matthess    Albert      NEW       626.00  626.00
H8578       5V00XW9VF13  90004242901  Dandy       Dean        RENEW     313.00  286.92
H8578       9RH7U95AX53  90004223101  Georgeson   Melinda     RENEW     313.00  286.92
Sub Total: 1,252.00 1,199.84
"""
    
    print("📄 HNE PDF Text:")
    print(hne_pdf_text)
    
    print("\n🔍 IMPROVED EXTRACTION LOGIC:")
    
    # Pattern to extract HNE commission entries
    import re
    
    # Look for H-code pattern followed by transaction ID, member ID, names, and amounts
    hne_pattern = r'(H\d{4})\s+(\w+)\s+(\d{11})\s+(\w+)\s+(\w+)\s+\w+\s+[\d.]+\s+([\d.]+)'
    
    matches = re.findall(hne_pattern, hne_pdf_text)
    
    print(f"   Found {len(matches)} commission entries:")
    
    extracted_entries = []
    for i, match in enumerate(matches, 1):
        h_code, txn_id, member_id, last_name, first_name, payout_amount = match
        
        entry = {
            'policy_number': member_id,  # Use the 11-digit Member ID as policy number
            'commission_amount': float(payout_amount),
            'member_name': f"{first_name} {last_name}",
            'h_code': h_code,
            'txn_id': txn_id,
            'date': '2025-07-01'  # Default date
        }
        
        extracted_entries.append(entry)
        print(f"      Entry {i}: Policy={member_id} | Amount=${payout_amount} | Member={first_name} {last_name}")
    
    print(f"\n✅ EXTRACTED {len(extracted_entries)} ENTRIES (should be 3)")
    
    # Verify against expected enrollment data
    expected_policies = {
        '90004932901': ('Matthess Albert', 300.00),
        '90004242901': ('Dandy Dean', 650.00),
        '90004223101': ('Georgeson Melinda', 280.00)
    }
    
    print("\n🔍 COMPARING WITH EXPECTED ENROLLMENT:")
    for entry in extracted_entries:
        policy = entry['policy_number']
        actual_amount = entry['commission_amount']
        member = entry['member_name']
        
        if policy in expected_policies:
            expected_member, expected_amount = expected_policies[policy]
            print(f"   ✅ Policy {policy}: Found ${actual_amount} (expected ${expected_amount}) | Member: {member}")
        else:
            print(f"   ❌ Policy {policy}: Unexpected policy found")
    
    # Check for missing policies
    extracted_policies = {entry['policy_number'] for entry in extracted_entries}
    for policy, (expected_member, expected_amount) in expected_policies.items():
        if policy not in extracted_policies:
            print(f"   ❌ MISSING: Policy {policy} ({expected_member}) with expected ${expected_amount}")
    
    print("\n🎯 RESULT:")
    if len(extracted_entries) == 3:
        print("   ✅ SUCCESS: All 3 commission entries extracted!")
        print("   ✅ This should fix the $0.00 subscriber total issue")
    else:
        print(f"   ❌ ISSUE: Only {len(extracted_entries)} entries extracted (expected 3)")
    
    return extracted_entries

if __name__ == "__main__":
    test_improved_hne_extraction()