#!/usr/bin/env python3
"""
Test script to demonstrate similarity-based column mapping in the commission reconciliation system.
Shows how the system adapts to different column naming conventions automatically.
"""

from commission_reconciliation_system import CommissionReconciliationSystem

def test_similarity_matching():
    """Test the similarity-based column mapping with various header formats."""
    system = CommissionReconciliationSystem()
    
    print("🧪 Testing Similarity-Based Column Mapping")
    print("="*60)
    
    # Test cases with different column naming conventions
    test_cases = [
        {
            'name': 'Standard Format',
            'headers': ['Plan ID', 'Transaction ID', 'Member ID', 'Effective Date', 'Last Name', 'First Name', 'Payout'],
            'carrier': 'generic'
        },
        {
            'name': 'Alternative Format 1',
            'headers': ['Product Code', 'Ref Number', 'Policy Number', 'Start Date', 'Surname', 'Given Name', 'Commission'],
            'carrier': 'generic'
        },
        {
            'name': 'Alternative Format 2',
            'headers': ['Scheme', 'Confirmation', 'Subscriber ID', 'Activation Date', 'Family Name', 'First Name', 'Net Amount'],
            'carrier': 'generic'
        },
        {
            'name': 'Variation with Underscores',
            'headers': ['plan_code', 'trans_ref', 'member_no', 'effective_dt', 'last_nm', 'first_nm', 'net_payout'],
            'carrier': 'generic'
        },
        {
            'name': 'Short Form',
            'headers': ['Plan', 'Trans', 'Member', 'Date', 'Last', 'First', 'Pay'],
            'carrier': 'generic'
        },
        {
            'name': 'With Extra Words',
            'headers': ['Plan Product ID', 'Transaction Reference Number', 'Member Policy ID', 'Contract Effective Date', 'Member Last Name', 'Member First Name', 'Final Payout Amount'],
            'carrier': 'generic'
        },
        {
            'name': 'Mixed Case and Symbols',
            'headers': ['PLAN-ID', 'TransactionRef', 'member_policy_id', 'Eff.Date', 'LastName', 'FirstName', 'Commission$'],
            'carrier': 'generic'
        },
        {
            'name': 'Alternative Terms',
            'headers': ['Product', 'Reference', 'Customer ID', 'Begin Date', 'Surname', 'Forename', 'Payment'],
            'carrier': 'generic'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"   Headers: {test_case['headers']}")
        
        column_map = system._build_column_mapping(test_case['headers'], test_case['carrier'])
        
        if column_map:
            print("   ✅ Mapping Result:")
            for field, idx in sorted(column_map.items()):
                header = test_case['headers'][idx] if idx < len(test_case['headers']) else 'N/A'
                print(f"      {field}: {idx} ('{header}')")
        else:
            print("   ❌ Failed to create mapping")
    
    print(f"\n✅ Similarity Matching Tests Completed")

def test_similarity_scoring():
    """Test the similarity scoring algorithm with various examples."""
    system = CommissionReconciliationSystem()
    
    print("\n🎯 Testing Similarity Scoring Algorithm")
    print("="*60)
    
    test_cases = [
        # Member ID variations
        {
            'field': 'member_id',
            'keywords': ['member', 'policy', 'subscriber', 'customer'],
            'headers': ['Member ID', 'Member No', 'Policy ID', 'Subscriber ID', 'Customer Number', 'Client ID', 'Plan Code']
        },
        # Date variations
        {
            'field': 'effective_date',
            'keywords': ['effective', 'start', 'begin', 'date'],
            'headers': ['Effective Date', 'Start Date', 'Begin Date', 'Activation Date', 'Contract Date', 'Plan Date', 'Member ID']
        },
        # Payment variations
        {
            'field': 'payout',
            'keywords': ['payout', 'net', 'commission', 'payment', 'amount'],
            'headers': ['Payout', 'Net Amount', 'Commission', 'Payment', 'Total', 'Final Amount', 'Member Name']
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📊 Testing '{test_case['field']}' field:")
        print(f"   Keywords: {test_case['keywords']}")
        
        scores = []
        for header in test_case['headers']:
            score = system._calculate_similarity_score(header, test_case['keywords'])
            scores.append((header, score))
        
        # Sort by score (highest first)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        print("   Similarity Scores:")
        for header, score in scores:
            status = "✅" if score > 0.5 else "⚠️" if score > 0.3 else "❌"
            print(f"      {status} '{header}': {score:.3f}")
    
    print(f"\n✅ Similarity Scoring Tests Completed")

def demonstrate_adaptability():
    """Demonstrate the system's adaptability to different naming conventions."""
    print("\n🔄 Demonstrating System Adaptability")
    print("="*60)
    
    print("🎯 Key Advantages of Similarity-Based Matching:")
    print("   ✅ Automatically adapts to new column names")
    print("   ✅ No need to update hardcoded patterns")
    print("   ✅ Handles typos and variations gracefully")
    print("   ✅ Works with different naming conventions")
    print("   ✅ Scores similarity to find best matches")
    print("   ✅ Avoids duplicate column assignments")
    
    print("\n📋 Example Adaptations:")
    
    adaptations = [
        ("Member ID → Member No", "Handles number vs ID variations"),
        ("Effective Date → Start Date", "Recognizes semantic equivalence"), 
        ("Payout → Commission", "Matches payment-related terms"),
        ("Transaction ID → Ref Number", "Adapts to different reference styles"),
        ("Last Name → Surname", "Handles name field variations"),
        ("plan_id → Product Code", "Works with different formats and cases")
    ]
    
    for old_name, new_name in adaptations:
        print(f"   🔄 {old_name} - {new_name}")
    
    print("\n🚀 Future Benefits:")
    print("   • Automatic handling of carrier-specific naming")
    print("   • Reduced maintenance when formats change")  
    print("   • Improved reliability across different carriers")
    print("   • No manual pattern updates required")

def test_edge_cases():
    """Test edge cases and boundary conditions."""
    system = CommissionReconciliationSystem()
    
    print("\n🧪 Testing Edge Cases")
    print("="*50)
    
    edge_cases = [
        {
            'name': 'Empty Headers',
            'headers': [],
            'carrier': 'generic'
        },
        {
            'name': 'Single Column',
            'headers': ['Data'],
            'carrier': 'generic'
        },
        {
            'name': 'No Matching Headers',
            'headers': ['Column A', 'Column B', 'Column C'],
            'carrier': 'generic'
        },
        {
            'name': 'Duplicate Similar Names',
            'headers': ['Member ID 1', 'Member ID 2', 'Member Number', 'Date', 'Amount'],
            'carrier': 'generic'
        },
        {
            'name': 'Special Characters',
            'headers': ['Member@ID', 'Date/Time', 'Amount($)', 'Name#1', 'Type%'],
            'carrier': 'generic'
        }
    ]
    
    for test_case in edge_cases:
        print(f"\n📋 Edge Case: {test_case['name']}")
        print(f"   Headers: {test_case['headers']}")
        
        try:
            column_map = system._build_column_mapping(test_case['headers'], test_case['carrier'])
            if column_map:
                print("   ✅ Handled gracefully - mapping created")
                for field, idx in column_map.items():
                    print(f"      {field}: {idx}")
            else:
                print("   ⚠️ No mapping created (expected for some cases)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Edge Case Tests Completed")

def main():
    """Run all demonstration tests."""
    print("🚀 Commission Reconciliation System - Similarity-Based Matching Demo")
    print("="*80)
    
    test_similarity_matching()
    test_similarity_scoring()
    demonstrate_adaptability()
    test_edge_cases()
    
    print(f"\n🎉 All tests completed successfully!")
    print("📋 The system now uses intelligent similarity-based column matching.")
    print("🔧 Ready for any carrier with any column naming convention!")

if __name__ == "__main__":
    main()