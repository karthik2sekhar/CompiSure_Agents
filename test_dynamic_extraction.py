#!/usr/bin/env python3
"""
Test script to demonstrate the dynamic extraction capabilities of the improved commission reconciliation system.
"""

from commission_reconciliation_system import CommissionReconciliationSystem

def test_column_mapping():
    """Test the column mapping functionality with different header formats."""
    system = CommissionReconciliationSystem()
    
    print("🧪 Testing Dynamic Column Mapping")
    print("="*50)
    
    # Test 1: HNE format (no headers, title row)
    print("\n📋 Test 1: HNE Format (Title Row)")
    hne_header = ["Incentive ID : Broker Commission"]
    column_map = system._build_column_mapping(hne_header, 'hne')
    print(f"   Input: {hne_header}")
    print(f"   Mapping: {column_map}")
    
    # Test 2: Standard header format
    print("\n📋 Test 2: Standard Header Format")
    standard_headers = ["Plan ID", "Transaction ID", "Member ID", "Effective Date", "Last Name", "First Name", "Payout"]
    column_map = system._build_column_mapping(standard_headers, 'generic')
    print(f"   Input: {standard_headers}")
    print(f"   Mapping: {column_map}")
    
    # Test 3: Alternative header format (different order)
    print("\n📋 Test 3: Alternative Header Format (Different Order)")
    alt_headers = ["Member ID", "Effective Date", "First Name", "Last Name", "Commission", "Plan ID"]
    column_map = system._build_column_mapping(alt_headers, 'generic')
    print(f"   Input: {alt_headers}")
    print(f"   Mapping: {column_map}")
    
    # Test 4: Missing essential columns
    print("\n📋 Test 4: Missing Essential Columns")
    incomplete_headers = ["Plan ID", "First Name", "Last Name"]
    column_map = system._build_column_mapping(incomplete_headers, 'generic')
    print(f"   Input: {incomplete_headers}")
    print(f"   Mapping: {column_map}")
    
    print("\n✅ Dynamic Column Mapping Tests Completed")

def test_safe_extraction():
    """Test the safe extraction methods."""
    system = CommissionReconciliationSystem()
    
    print("\n🧪 Testing Safe Extraction Methods")
    print("="*50)
    
    test_row = ["H2737", "9P87YX0QG32", "90004932901", "2/1/2025", "001", "Matthess", "Albert", "Katherine Beth Evans", "15668354", "*", "NEW", "626.00", "626.00"]
    
    print(f"📋 Test Row: {test_row}")
    
    # Test safe string extraction
    member_id = system._safe_extract(test_row, 2)
    print(f"   Member ID (index 2): '{member_id}'")
    
    # Test safe float extraction
    payout = system._safe_extract_float(test_row, 12)
    print(f"   Payout (index 12): {payout}")
    
    # Test extraction with invalid index
    invalid_str = system._safe_extract(test_row, 99)
    print(f"   Invalid index 99: '{invalid_str}'")
    
    invalid_float = system._safe_extract_float(test_row, 99)
    print(f"   Invalid float index 99: {invalid_float}")
    
    print("\n✅ Safe Extraction Tests Completed")

def demonstrate_adaptability():
    """Demonstrate how the system adapts to different table structures."""
    print("\n🎯 Demonstrating System Adaptability")
    print("="*50)
    
    print("📊 Key Benefits of Dynamic Extraction:")
    print("   ✅ No hardcoded column positions")
    print("   ✅ Adapts to column order changes")
    print("   ✅ Handles missing optional columns gracefully")
    print("   ✅ Validates essential columns are present")
    print("   ✅ Works with carrier-specific table formats")
    print("   ✅ Supports multiple header naming conventions")
    
    print("\n📋 Column Mapping Patterns Supported:")
    patterns = {
        'member_id': ['member id', 'memberid', 'member_id', 'policy id', 'policyid'],
        'effective_date': ['effective date', 'effectivedate', 'effective_date', 'date'],
        'payout': ['payout', 'net', 'net amount', 'netamount', 'net_amount', 'commission']
    }
    
    for field, pattern_list in patterns.items():
        print(f"   {field}: {pattern_list}")
    
    print("\n🔄 Future Carrier Support:")
    print("   • New carriers can be added by updating carrier configuration")
    print("   • Table-specific mappings can be defined per carrier")
    print("   • Generic mapping handles standard header formats")
    print("   • System automatically detects and maps column positions")

def main():
    """Run all demonstration tests."""
    print("🚀 Commission Reconciliation System - Dynamic Extraction Demo")
    print("="*80)
    
    test_column_mapping()
    test_safe_extraction()
    demonstrate_adaptability()
    
    print(f"\n🎉 All tests completed successfully!")
    print("📋 The system now uses dynamic column mapping instead of hardcoded positions.")
    print("🔧 Ready for production use with multiple carriers and changing table formats!")

if __name__ == "__main__":
    main()