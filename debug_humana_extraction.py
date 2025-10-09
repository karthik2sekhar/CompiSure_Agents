#!/usr/bin/env python3
"""
Debug script to test Humana extraction and identify why policy numbers are wrong.
"""

import json
import os
import sys

# Mock the LLM response that we expect based on the prompt
expected_llm_response = """
[
  {
    "policy_number": "00000790462A",
    "amount": 43.57,
    "date": "2025-07-01",
    "member_name": "Norris William",
    "product_name": "Medicare",
    "premium": null
  },
  {
    "policy_number": "00000788617A", 
    "amount": 43.57,
    "date": "2025-07-01",
    "member_name": "Neill Kathleen",
    "product_name": "Medicare",
    "premium": null
  }
]
"""

# Current buggy LLM response (what's actually happening)
actual_llm_response = """
[
  {
    "policy_number": "Norris William",
    "amount": 43.57,
    "date": "2025-07-01",
    "member_name": "Norris William",
    "product_name": "Medicare",
    "premium": null
  },
  {
    "policy_number": "Neill Kathleen",
    "amount": 43.57,
    "date": "2025-07-01", 
    "member_name": "Neill Kathleen",
    "product_name": "Medicare",
    "premium": null
  }
]
"""

print("=== HUMANA EXTRACTION DEBUG ===")
print("\n1. Expected LLM Response (correct policy numbers):")
expected_data = json.loads(expected_llm_response.strip())
for entry in expected_data:
    print(f"   Policy: {entry['policy_number']} | Member: {entry['member_name']} | Amount: ${entry['amount']}")

print("\n2. Actual LLM Response (incorrect - using names as policy numbers):")
actual_data = json.loads(actual_llm_response.strip())  
for entry in actual_data:
    print(f"   Policy: {entry['policy_number']} | Member: {entry['member_name']} | Amount: ${entry['amount']}")

print("\n3. Enrollment Data for Matching:")
enrollment_data = [
    {'policy_number': '00000790462A', 'member_name': 'Norris William N', 'commission_amount': 300.00},
    {'policy_number': '00000788617A', 'member_name': "O'Neill Kathleen M", 'commission_amount': 300.00}
]

for entry in enrollment_data:
    print(f"   Policy: {entry['policy_number']} | Member: {entry['member_name']} | Expected: ${entry['commission_amount']}")

print("\n4. Reconciliation Outcome:")
print("   With CORRECT extraction → Policy numbers match → Commissions reconcile properly")
print("   With BUGGY extraction → Policy numbers don't match → Shows $0.00 commissions")

print("\n5. The Problem:")
print("   - LLM is returning member names in the 'policy_number' field")  
print("   - This causes policy number mismatch during reconciliation")
print("   - Result: 'Subscriber total $0.00' in reports")

print("\n6. Solution:")
print("   - Fix LLM prompt to be more explicit about policy number format")
print("   - Add validation to catch when policy numbers look like names")
print("   - Add post-processing to swap fields if policy_number contains spaces/names")