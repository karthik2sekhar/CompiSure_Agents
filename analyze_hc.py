#!/usr/bin/env python3

# Quick analysis of the HC commission extraction
import json

# Read the latest reconciliation data
with open('reports/commission_reconciliation_data_20251006_111508.json', 'r') as f:
    data = json.load(f)

print("HC Commission Analysis")
print("=" * 50)

hc_data = data.get('hc', {})
print(f"Total Commissions Extracted: ${hc_data.get('total_commissions', 0):.2f}")
print(f"Expected Commissions: ${hc_data.get('expected_commissions', 0):.2f}")
print(f"Variance: ${hc_data.get('variance_amount', 0):.2f}")

# Group commissions by policy to understand the structure
if 'extracted_commissions' in hc_data:
    policy_totals = {}
    for comm in hc_data['extracted_commissions']:
        policy = comm.get('policy_number', 'unknown')
        amount = comm.get('actual_commission', 0)
        if policy not in policy_totals:
            policy_totals[policy] = 0
        policy_totals[policy] += amount
    
    print(f"\nCommissions by Policy Group:")
    for policy, total in sorted(policy_totals.items()):
        print(f"  {policy}: ${total:.2f}")
    
    print(f"\nTotal policies with commissions: {len(policy_totals)}")
    print(f"Average commission per policy: ${sum(policy_totals.values()) / len(policy_totals):.2f}")