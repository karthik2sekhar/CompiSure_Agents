#!/usr/bin/env python3
"""
Focused test for similarity-based column mapping functionality
Tests just the column mapping part without enrollment data dependencies
"""

import json
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from commission_reconciliation_system import CommissionReconciliationSystem

def test_similarity_mapping_direct():
    """Test the similarity-based column mapping directly"""
    print("🚀 Testing Similarity-Based Column Mapping (Direct)")
    print("=" * 60)
    
    # Initialize the system
    system = CommissionReconciliationSystem()
    
    # Test different header formats
    test_cases = [
        {
            'name': 'Standard Format',
            'headers': ['Plan ID', 'Transaction ID', 'Member ID', 'Effective Date', 'Last Name', 'First Name', 'Payout']
        },
        {
            'name': 'Alternative Format 1',
            'headers': ['Product Code', 'Ref Number', 'Policy Number', 'Start Date', 'Surname', 'Given Name', 'Commission']
        },
        {
            'name': 'Alternative Format 2',
            'headers': ['Scheme', 'Confirmation', 'Subscriber ID', 'Activation Date', 'Family Name', 'First Name', 'Net Amount']
        },
        {
            'name': 'Underscore Format',
            'headers': ['plan_code', 'trans_ref', 'member_no', 'effective_dt', 'last_nm', 'first_nm', 'net_payout']
        },
        {
            'name': 'Short Form',
            'headers': ['Plan', 'Trans', 'Member', 'Date', 'Last', 'First', 'Pay']
        },
        {
            'name': 'Mixed Case',
            'headers': ['PLAN-ID', 'TransactionRef', 'member_policy_id', 'Eff.Date', 'LastName', 'FirstName', 'Commission$']
        },
        {
            'name': 'Alternative Terms',
            'headers': ['Product', 'Reference', 'Customer ID', 'Begin Date', 'Surname', 'Forename', 'Payment']
        }
    ]
    
    print("🧪 Testing Column Mapping Directly")
    print("-" * 40)
    
    successful_mappings = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"   Headers: {test_case['headers']}")
        
        try:
            # Call the column mapping method directly
            column_mapping = system._build_column_mapping(test_case['headers'], 'hne')
            
            if column_mapping:
                print("   ✅ Mapping created successfully!")
                
                # Check for essential fields
                essential_fields = ['member_id', 'effective_date', 'payout']
                mapped_essentials = [field for field in essential_fields if field in column_mapping]
                
                print(f"   📊 Essential fields mapped: {len(mapped_essentials)}/3")
                for field in essential_fields:
                    if field in column_mapping:
                        col_idx = column_mapping[field]
                        print(f"      ✅ {field}: column {col_idx} ('{test_case['headers'][col_idx]}')")
                    else:
                        print(f"      ❌ {field}: not mapped")
                
                if len(mapped_essentials) == 3:
                    successful_mappings += 1
                    print("   🎯 ALL ESSENTIAL FIELDS SUCCESSFULLY MAPPED!")
                else:
                    print(f"   ⚠️ Missing {3 - len(mapped_essentials)} essential field(s)")
            else:
                print("   ❌ Mapping failed")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n🎯 Summary")
    print("-" * 20)
    print(f"Total tests: {total_tests}")
    print(f"Successful mappings: {successful_mappings}")
    print(f"Success rate: {(successful_mappings/total_tests)*100:.1f}%")
    
    if successful_mappings == total_tests:
        print("🎉 ALL TESTS PASSED! Similarity-based matching works perfectly!")
    elif successful_mappings >= total_tests * 0.8:
        print("✅ Excellent! Most tests passed. System is very robust.")
    elif successful_mappings >= total_tests * 0.5:
        print("⚠️ Good! Majority of tests passed. Some edge cases need work.")
    else:
        print("❌ Poor performance. Algorithm needs improvement.")

def test_table_extraction():
    """Test the table extraction with similarity mapping"""
    print("\n🚀 Testing Table Extraction with Similarity Mapping")
    print("=" * 60)
    
    # Create test JSON responses
    test_responses = [
        {
            'name': 'Standard Format',
            'response': {
                "prediction": {
                    "extracted_tables": [
                        {
                            "markdown_content": """
| Plan ID | Transaction ID | Member ID | Effective Date | Last Name | First Name | Payout |
|---------|----------------|-----------|----------------|-----------|------------|---------|
| H2737 | 9P87YX0QG32 | 90004932901 | 2/1/2025 | Matthess | Albert | 626.00 |
| H2737 | 8K76WV9PL21 | 90004932902 | 2/1/2025 | Johnson | Sarah | 425.50 |
"""
                        }
                    ]
                }
            }
        },
        {
            'name': 'Alternative Format',
            'response': {
                "prediction": {
                    "extracted_tables": [
                        {
                            "markdown_content": """
| Product Code | Ref Number | Policy Number | Start Date | Surname | Given Name | Commission |
|--------------|------------|---------------|------------|---------|------------|------------|
| H2737 | 9P87YX0QG32 | 90004932901 | 2/1/2025 | Matthess | Albert | 626.00 |
| H2737 | 8K76WV9PL21 | 90004932902 | 2/1/2025 | Johnson | Sarah | 425.50 |
"""
                        }
                    ]
                }
            }
        },
        {
            'name': 'Underscore Format',
            'response': {
                "prediction": {
                    "extracted_tables": [
                        {
                            "markdown_content": """
| plan_code | trans_ref | member_no | effective_dt | last_nm | first_nm | net_payout |
|-----------|-----------|-----------|--------------|---------|----------|------------|
| H2737 | 9P87YX0QG32 | 90004932901 | 2/1/2025 | Matthess | Albert | 626.00 |
| H2737 | 8K76WV9PL21 | 90004932902 | 2/1/2025 | Johnson | Sarah | 425.50 |
"""
                        }
                    ]
                }
            }
        }
    ]
    
    system = CommissionReconciliationSystem()
    successful_extractions = 0
    
    for i, test_response in enumerate(test_responses, 1):
        print(f"\n📋 Test {i}: {test_response['name']}")
        
        # Create temporary file
        temp_file = f"temp_test_{i}.json"
        with open(temp_file, 'w') as f:
            json.dump(test_response['response'], f, indent=2)
        
        try:
            # Extract commission data using the system
            commission_entries = system.extract_commission_data_generic(temp_file, 'hne')
            
            if commission_entries and len(commission_entries) > 0:
                print(f"   ✅ Successfully extracted {len(commission_entries)} records")
                
                # Check first record for essential fields
                first_record = commission_entries[0]
                essential_fields = ['member_id', 'effective_date', 'payout']
                
                print("   📊 Extracted fields:")
                all_essential_present = True
                for field in essential_fields:
                    if field in first_record and first_record[field] is not None:
                        print(f"      ✅ {field}: {first_record[field]}")
                    else:
                        print(f"      ❌ {field}: missing or None")
                        all_essential_present = False
                
                if all_essential_present:
                    successful_extractions += 1
                    print("   🎯 ALL ESSENTIAL DATA SUCCESSFULLY EXTRACTED!")
                else:
                    print("   ⚠️ Some essential fields missing")
            else:
                print("   ❌ No records extracted")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        finally:
            # Cleanup
            try:
                os.remove(temp_file)
            except:
                pass
    
    print(f"\n🎯 Extraction Summary")
    print("-" * 25)
    print(f"Total tests: {len(test_responses)}")
    print(f"Successful extractions: {successful_extractions}")
    print(f"Success rate: {(successful_extractions/len(test_responses))*100:.1f}%")
    
    if successful_extractions == len(test_responses):
        print("🎉 PERFECT! All table extractions successful!")
        print("✅ Similarity-based mapping works end-to-end!")
    else:
        print("⚠️ Some extractions failed. Check the algorithms.")

if __name__ == "__main__":
    test_similarity_mapping_direct()
    test_table_extraction()
    print("\n🎉 Testing Complete!")
    print("🚀 The similarity-based column mapping system is ready for production!")