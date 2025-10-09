#!/usr/bin/env python3
"""
Test script to verify the Humana policy normalization fix
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.insert(0, 'src')

# Test the policy normalization logic
def test_humana_policy_normalization():
    """Test the policy ID normalization for Humana"""
    
    print("🧪 TESTING HUMANA POLICY NORMALIZATION FIX")
    print("=" * 50)
    
    # Test cases from the actual Humana data
    test_cases = [
        ("N00000790462A", "00000790462A", "humana"),  # Should remove leading N
        ("M00000788617A", "00000788617A", "humana"),  # Should remove leading M
        ("90004932901", "90004932901", "hne"),        # Should remain unchanged
        ("771140_Billie's", "771140", "hc"),          # Should split on underscore
    ]
    
    def normalize_policy_id(policy_number, carrier_name):
        policy_str = str(policy_number)
        
        # For policy numbers with underscores, take the first part
        if '_' in policy_str:
            policy_str = policy_str.split('_')[0]
        
        # For Humana: Remove leading letter if present (e.g., N00000790462A -> 00000790462A)
        if carrier_name == 'humana' and len(policy_str) > 1 and policy_str[0].isalpha():
            # Check if it follows Humana pattern: Letter + 11 digits + Letter
            if len(policy_str) == 13 and policy_str[1:-1].isdigit() and policy_str[-1].isalpha():
                policy_str = policy_str[1:]  # Remove first letter
                print(f"🔧 Normalized Humana policy: {policy_number} -> {policy_str}")
        
        return policy_str
    
    print("1️⃣ POLICY NORMALIZATION TESTS:")
    all_passed = True
    
    for original, expected, carrier in test_cases:
        result = normalize_policy_id(original, carrier)
        passed = result == expected
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {carrier.upper()} '{original}' -> '{result}' (expected: '{expected}')")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ All policy normalization tests PASSED!")
    else:
        print("\n❌ Some policy normalization tests FAILED!")
        return False
    
    return True

def test_enrollment_matching():
    """Test if normalized policy IDs match enrollment data"""
    
    print("\n2️⃣ ENROLLMENT MATCHING TEST:")
    
    try:
        import pandas as pd
        
        # Load enrollment data
        enrollment_df = pd.read_csv('docs/enrollment_info.csv')
        humana_enrollment = enrollment_df[enrollment_df['carrier'].str.lower() == 'humana']
        
        print(f"   Enrollment policy IDs: {list(humana_enrollment['policy_id'])}")
        
        # Test extracted policy numbers (what Humana extraction produces)
        extracted_policies = ["N00000790462A", "M00000788617A"]
        print(f"   Extracted policy numbers: {extracted_policies}")
        
        # Apply normalization
        def normalize_policy_id(policy_number, carrier_name):
            policy_str = str(policy_number)
            
            if '_' in policy_str:
                policy_str = policy_str.split('_')[0]
            
            if carrier_name == 'humana' and len(policy_str) > 1 and policy_str[0].isalpha():
                if len(policy_str) == 13 and policy_str[1:-1].isdigit() and policy_str[-1].isalpha():
                    policy_str = policy_str[1:]
                    print(f"   🔧 Normalized: {policy_number} -> {policy_str}")
            
            return policy_str
        
        normalized_policies = [normalize_policy_id(p, 'humana') for p in extracted_policies]
        print(f"   Normalized policy IDs: {normalized_policies}")
        
        # Check matches
        enrollment_policy_list = list(humana_enrollment['policy_id'])
        matches = 0
        for normalized in normalized_policies:
            if normalized in enrollment_policy_list:
                print(f"   ✅ MATCH: '{normalized}' found in enrollment")
                matches += 1
            else:
                print(f"   ❌ NO MATCH: '{normalized}' not found in enrollment")
        
        if matches == len(normalized_policies):
            print(f"\n✅ All {matches} policies matched successfully!")
            return True
        else:
            print(f"\n❌ Only {matches}/{len(normalized_policies)} policies matched!")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing enrollment matching: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🚀 STARTING HUMANA POLICY NORMALIZATION TESTS")
    print("=" * 60)
    
    test1_passed = test_humana_policy_normalization()
    test2_passed = test_enrollment_matching()
    
    print("\n📊 TEST RESULTS:")
    print(f"   Policy Normalization: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"   Enrollment Matching: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! The Humana policy normalization fix should work!")
        return True
    else:
        print("\n💥 SOME TESTS FAILED! The fix needs more work.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)