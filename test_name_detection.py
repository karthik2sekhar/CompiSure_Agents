#!/usr/bin/env python3
"""
Test script to validate the Humana policy number extraction fix.
"""

import sys
import os
sys.path.append('src')

from src.llm_extraction_service import LLMExtractionService

def test_name_detection():
    """Test that the name detection works correctly."""
    service = LLMExtractionService()
    
    print("=== TESTING NAME DETECTION ===")
    
    # Test cases - names that should be detected as names (not policy numbers)
    names = [
        "Norris William",
        "Neill Kathleen", 
        "John Smith",
        "Mary Johnson",
        "Robert Brown",
        "Jane Doe"
    ]
    
    # Test cases - policy numbers that should NOT be detected as names
    policy_numbers = [
        "00000790462A",
        "00000788617A",
        "90004932901",
        "H2737",
        "771140",
        "N00000790462A"
    ]
    
    print("\n1. Names (should be detected as names):")
    for name in names:
        is_name = service._looks_like_person_name(name)
        status = "✅ CORRECT" if is_name else "❌ MISSED"
        print(f"   '{name}' → {is_name} {status}")
    
    print("\n2. Policy Numbers (should NOT be detected as names):")
    for policy in policy_numbers:
        is_name = service._looks_like_person_name(policy)
        status = "✅ CORRECT" if not is_name else "❌ FALSE POSITIVE"
        print(f"   '{policy}' → {is_name} {status}")

def test_entry_cleaning():
    """Test that entry cleaning detects and flags name-as-policy issues."""
    service = LLMExtractionService()
    
    print("\n=== TESTING ENTRY CLEANING ===")
    
    # Simulate what the LLM is currently returning (incorrect)
    bad_entries = [
        {
            "policy_number": "Norris William",
            "amount": 43.57,
            "date": "2025-07-01",
            "member_name": "Norris William",
            "product_name": "Medicare"
        },
        {
            "policy_number": "Neill Kathleen",
            "amount": 43.57,
            "date": "2025-07-01", 
            "member_name": "Neill Kathleen",
            "product_name": "Medicare"
        }
    ]
    
    # What the LLM should return (correct)
    good_entries = [
        {
            "policy_number": "00000790462A",
            "amount": 43.57,
            "date": "2025-07-01",
            "member_name": "Norris William",
            "product_name": "Medicare"
        },
        {
            "policy_number": "00000788617A",
            "amount": 43.57,
            "date": "2025-07-01",
            "member_name": "Neill Kathleen", 
            "product_name": "Medicare"
        }
    ]
    
    print("\n1. Processing BAD entries (names as policy numbers):")
    for i, entry in enumerate(bad_entries):
        print(f"\n   Entry {i+1}: {entry}")
        cleaned = service._clean_entry(entry)
        print(f"   Cleaned: {cleaned}")
        if 'extraction_error' in cleaned:
            print(f"   ✅ ERROR DETECTED: {cleaned['extraction_error']}")
        else:
            print(f"   ❌ ERROR NOT DETECTED")
    
    print("\n2. Processing GOOD entries (correct policy numbers):")
    for i, entry in enumerate(good_entries):
        print(f"\n   Entry {i+1}: {entry}")
        cleaned = service._clean_entry(entry)
        print(f"   Cleaned: {cleaned}")
        if 'extraction_error' in cleaned:
            print(f"   ❌ FALSE POSITIVE: {cleaned['extraction_error']}")
        else:
            print(f"   ✅ NO ERROR (correct)")

if __name__ == "__main__":
    test_name_detection()
    test_entry_cleaning()
    
    print("\n=== SUMMARY ===")
    print("✅ Added name detection to identify when LLM uses names as policy numbers")
    print("✅ Added validation in entry cleaning to flag these issues")
    print("✅ Added detailed logging to help debug extraction problems")
    print("📋 Next step: Test with actual Humana PDF extraction")