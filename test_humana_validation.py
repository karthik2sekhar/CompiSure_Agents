#!/usr/bin/env python3
"""
Test Humana extraction with our improved validation.
"""

import sys
import os
sys.path.append('src')

from src.llm_extraction_service import LLMExtractionService

def main():
    print("=== TESTING HUMANA EXTRACTION WITH VALIDATION ===")
    
    # Create service
    service = LLMExtractionService()
    
    # Simulate the buggy LLM response that we've been seeing
    mock_response = """
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
    
    print("1. Processing mock LLM response (simulating current buggy behavior):")
    print(f"   Raw response: {mock_response.strip()}")
    
    # Parse the response using our validation system
    entries = service._parse_llm_response(mock_response)
    
    print(f"\n2. Parsed entries ({len(entries)} found):")
    for i, entry in enumerate(entries, 1):
        print(f"   Entry {i}: {entry}")
        if 'extraction_error' in entry:
            print(f"      🚨 EXTRACTION ERROR: {entry['extraction_error']}")
    
    print("\n3. What happens during reconciliation:")
    print("   - These entries have policy_number='INVALID_NAME_...'")
    print("   - Reconciliation won't match them with enrollment data")
    print("   - Result: 'Subscriber total $0.00' in reports")
    
    print("\n4. The Fix:")
    print("   - Our validation system now detects this issue")
    print("   - We log clear error messages")
    print("   - Next step: Improve the LLM prompt to prevent this")

if __name__ == "__main__":
    main()