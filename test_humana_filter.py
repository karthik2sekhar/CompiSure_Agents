#!/usr/bin/env python3
"""
Test Humana filtering logic
"""
import re

# Sample entries as extracted by LLM
test_entries = [
    {"policy_number": "Evans Katherine", "commission_amount": 87.14},
    {"policy_number": "Norris William", "commission_amount": 43.57},
    {"policy_number": "Neill Kathleen", "commission_amount": 43.57}
]

def test_filter_logic():
    """Test the filtering logic"""
    
    for entry in test_entries:
        policy_number = str(entry.get('policy_number', '')).strip()
        amount = float(entry.get('commission_amount', 0))
        
        print(f"\nTesting: {policy_number} (${amount})")
        
        # Test pattern matching
        pattern1 = re.search(r'[A-Z]\d{8,}[A-Z]', policy_number)
        pattern2 = re.search(r'\d{6,}', policy_number)
        has_digits = any(char.isdigit() for char in policy_number)
        word_count = len(policy_number.split())
        
        print(f"  - Pattern [A-Z]\\d{{8,}}[A-Z]: {pattern1}")
        print(f"  - Pattern \\d{{6,}}: {pattern2}")
        print(f"  - Has digits: {has_digits}")
        print(f"  - Word count: {word_count}")
        
        # Current filter logic
        is_summary = (
            not re.search(r'[A-Z]\d{8,}[A-Z]', policy_number) and 
            not re.search(r'\d{6,}', policy_number) and
            len(policy_number.split()) <= 2
        )
        
        print(f"  - Would be filtered as summary: {is_summary}")

def appears_to_be_summary_amount(amount: float, all_entries: list) -> bool:
    """Check if an amount appears to be a summary total"""
    try:
        amount = float(amount)
        other_amounts = []
        
        for entry in all_entries:
            entry_amount = float(entry.get('commission_amount', 0))
            if entry_amount != amount:  # Don't include the current amount
                other_amounts.append(entry_amount)
        
        # Check if this amount equals the sum of other amounts (within small tolerance)
        other_total = sum(other_amounts)
        tolerance = 0.01  # Allow 1 cent difference for rounding
        
        return abs(amount - other_total) <= tolerance
        
    except (ValueError, TypeError):
        return False

if __name__ == "__main__":
    test_filter_logic()
    
    print(f"\n\nTesting summary amount logic:")
    for entry in test_entries:
        policy_number = entry.get('policy_number')
        amount = entry.get('commission_amount')
        is_summary_by_amount = appears_to_be_summary_amount(amount, test_entries)
        print(f"{policy_number}: ${amount} -> Summary by amount: {is_summary_by_amount}")