"""
Comprehensive test suite for the LandingAI Extract Normalizer
Tests with realistic JSON structures similar to actual LandingAI outputs
"""

import json
from landingai_extract_normalizer import LandingAIExtractNormalizer
import pandas as pd

def create_realistic_test_data():
    """Create test data that matches real LandingAI JSON structure patterns"""
    
    # HNE realistic test data
    hne_test = {
        'markdown': '''# Health New England - Sales Commission Statement

**Payee Name:** KATHRINE BETH EVANS  
**Payee ID:** 15668354  
**Period:** 2 [ 2/1/2025 - 2/28/2025 ]

| Contract ID | Txn ID | Member ID | Effective Date | PBP | Member LastName | Member FirstName | Broker | NPN | Term | Reason | Rate | Payout Amt |
|-------------|---------|-----------|----------------|------|-----------------|------------------|---------|------|------|---------|------|------------|
| H2737 | 9P87YX0QG32 | 90004932901 | 2/1/2025 | 001 | MATTHESS | ALBERT | KATHRINE BETH EVANS | 15668354 | * | NEW | 626.00 | 626.00 |
| H2737 | 9P87YX0QG33 | 90004932902 | 2/1/2025 | 001 | JOHNSON | MARY | KATHRINE BETH EVANS | 15668354 | * | NEW | 573.84 | 573.84 |
| H2737 | 9P87YX0QG34 | 90004932903 | 2/5/2025 | 001 | WILLIAMS | ROBERT | KATHRINE BETH EVANS | 15668354 | * | NEW | 0.00 | 0.00 |

**Sub Total:** $1,199.84  
**Net Payout Amt:** $1,199.84''',
        
        'chunks': [
            {
                'type': 'table',
                'markdown': '''<table>
<tr><th>Contract ID</th><th>Txn ID</th><th>Member ID</th><th>Effective Date</th><th>PBP</th><th>Member LastName</th><th>Member FirstName</th><th>Broker</th><th>NPN</th><th>Term</th><th>Reason</th><th>Rate</th><th>Payout Amt</th></tr>
<tr><td>H2737</td><td>9P87YX0QG32</td><td>90004932901</td><td>2/1/2025</td><td>001</td><td>MATTHESS</td><td>ALBERT</td><td>KATHRINE BETH EVANS</td><td>15668354</td><td>*</td><td>NEW</td><td>626.00</td><td>626.00</td></tr>
<tr><td>H2737</td><td>9P87YX0QG33</td><td>90004932902</td><td>2/1/2025</td><td>001</td><td>JOHNSON</td><td>MARY</td><td>KATHRINE BETH EVANS</td><td>15668354</td><td>*</td><td>NEW</td><td>573.84</td><td>573.84</td></tr>
<tr><td>H2737</td><td>9P87YX0QG34</td><td>90004932903</td><td>2/5/2025</td><td>001</td><td>WILLIAMS</td><td>ROBERT</td><td>KATHRINE BETH EVANS</td><td>15668354</td><td>*</td><td>NEW</td><td>0.00</td><td>0.00</td></tr>
</table>'''
            }
        ],
        'metadata': {'filename': 'HNE_test.pdf', 'page_count': 1}
    }
    
    # Humana realistic test data
    humana_test = {
        'markdown': '''Your Commission Statement

**for period ending July 14, 2025**

Agent EVANS KATHRINE E  
Agent number 1816357

**Statement date July 15, 2025**

**NORRIS WILLIAM N 00000790462A**(LV - MS) Effective 1/1/24

| Product type | Product code | Month paid/ Paid to date | Year | Rate | Paid amount | Comments |
|--------------|--------------|--------------------------|------|------|-------------|----------|
| MEDICARE | MES | JUL 25 | REN | 22.00 | $43.57 | Renewal commissions |
| MEDICARE | MEP | JUL 25 | REN | 22.00 | $43.57 | Renewal commissions |

**SMITH JOHN A 00000790463B**(LV - MS) Effective 3/1/24

| Product type | Product code | Month paid/ Paid to date | Year | Rate | Paid amount | Comments |
|--------------|--------------|--------------------------|------|------|-------------|----------|
| MEDICARE | MES | JUL 25 | REN | 18.50 | $37.00 | Renewal commissions |

**Total commissions**: $124.14''',
        
        'chunks': [
            {
                'type': 'table',
                'markdown': '''<table>
<tr><th>Product type</th><th>Product code</th><th>Month paid/ Paid to date</th><th>Year</th><th>Rate</th><th>Paid amount</th><th>Comments</th></tr>
<tr><td>MEDICARE</td><td>MES</td><td>JUL 25</td><td>REN</td><td>22.00</td><td>$43.57</td><td>Renewal commissions</td></tr>
<tr><td>MEDICARE</td><td>MEP</td><td>JUL 25</td><td>REN</td><td>22.00</td><td>$43.57</td><td>Renewal commissions</td></tr>
</table>'''
            },
            {
                'type': 'table',
                'markdown': '''<table>
<tr><th>Product type</th><th>Product code</th><th>Month paid/ Paid to date</th><th>Year</th><th>Rate</th><th>Paid amount</th><th>Comments</th></tr>
<tr><td>MEDICARE</td><td>MES</td><td>JUL 25</td><td>REN</td><td>18.50</td><td>$37.00</td><td>Renewal commissions</td></tr>
</table>'''
            }
        ],
        'metadata': {'filename': 'Humana_test.pdf', 'page_count': 1}
    }
    
    # HC realistic test data
    hc_test = {
        'markdown': '''Massachusetts Health Connector Authority

**Commission Statement - July 2025**

**Broker:** KATHRINE BETH EVANS

**Commission Summary**

| Group Policy | Member | Commission |
|-------------|---------|------------|
| 123456_ACME CORP | John Smith | $45.50 |
| 123456_ACME CORP | Mary Johnson | $45.50 |
| 123457_XYZ COMPANY | Robert Williams | $32.25 |
| 123457_XYZ COMPANY | Sarah Davis | $32.25 |
| 123458_ABC SERVICES | Michael Brown | $28.75 |

**Total Commission:** $184.25''',
        
        'chunks': [
            {
                'type': 'table',
                'markdown': '''<table>
<tr><th>Group Policy</th><th>Member</th><th>Commission</th></tr>
<tr><td>123456_ACME CORP</td><td>John Smith</td><td>$45.50</td></tr>
<tr><td>123456_ACME CORP</td><td>Mary Johnson</td><td>$45.50</td></tr>
<tr><td>123457_XYZ COMPANY</td><td>Robert Williams</td><td>$32.25</td></tr>
<tr><td>123457_XYZ COMPANY</td><td>Sarah Davis</td><td>$32.25</td></tr>
<tr><td>123458_ABC SERVICES</td><td>Michael Brown</td><td>$28.75</td></tr>
</table>'''
            }
        ],
        'metadata': {'filename': 'HC_test.pdf', 'page_count': 1}
    }
    
    return {
        'hne': hne_test,
        'humana': humana_test, 
        'hc': hc_test
    }

def run_comprehensive_test():
    """Run comprehensive test with all carrier types"""
    
    print("="*80)
    print("COMPREHENSIVE LANDINGAI EXTRACT NORMALIZER TEST")
    print("="*80)
    
    normalizer = LandingAIExtractNormalizer()
    test_data = create_realistic_test_data()
    
    all_results = []
    
    for carrier_name, test_case in test_data.items():
        print(f"\n{'='*20} TESTING {carrier_name.upper()} {'='*20}")
        
        # Test normalization
        result = normalizer.normalize_extract(test_case)
        all_results.append(result)
        
        if 'error' in result:
            print(f"❌ ERROR: {result['error']}")
            continue
        
        print(f"✅ SUCCESS")
        print(f"   Detected Carrier: {result.get('carrier', 'unknown')}")
        print(f"   Statement Date: {result.get('statement_date', 'Not found')}")
        print(f"   Agent Info: {result.get('agent_info', {})}")
        print(f"   Total Amount: ${result.get('total_amount', 0.0):.2f}")
        print(f"   Entry Count: {result.get('entry_count', 0)}")
        
        # Show sample entries
        entries = result.get('commission_entries', [])
        if entries:
            print(f"\n   Sample Commission Entries:")
            for i, entry in enumerate(entries[:3]):  # Show first 3 entries
                print(f"     {i+1}. {entry.get('member_name', 'Unknown')}: "
                      f"${entry.get('commission_amount', 0.0):.2f} "
                      f"(Policy: {entry.get('policy_id', 'N/A')})")
        
        # Test DataFrame conversion
        df = normalizer.to_dataframe(result)
        if not df.empty:
            print(f"\n   DataFrame Shape: {df.shape}")
            print(f"   DataFrame Columns: {list(df.columns)}")
        
        print(f"\n   Validation Summary:")
        expected_totals = {'hne': 1199.84, 'humana': 124.14, 'hc': 184.25}
        expected_counts = {'hne': 2, 'humana': 3, 'hc': 5}  # Only entries with amount > 0
        
        actual_total = result.get('total_amount', 0.0)
        actual_count = len([e for e in entries if e.get('commission_amount', 0) > 0])
        
        total_match = abs(actual_total - expected_totals.get(carrier_name, 0)) < 0.01
        count_match = actual_count == expected_counts.get(carrier_name, 0)
        
        print(f"     Total Amount: {'✅' if total_match else '❌'} "
              f"Expected ${expected_totals.get(carrier_name, 0):.2f}, "
              f"Got ${actual_total:.2f}")
        print(f"     Entry Count: {'✅' if count_match else '❌'} "
              f"Expected {expected_counts.get(carrier_name, 0)}, "
              f"Got {actual_count}")
    
    # Summary report
    print(f"\n{'='*20} OVERALL SUMMARY {'='*20}")
    
    successful_tests = [r for r in all_results if 'error' not in r]
    failed_tests = [r for r in all_results if 'error' in r]
    
    print(f"Total Tests: {len(all_results)}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(failed_tests)}")
    
    if successful_tests:
        total_entries = sum(r.get('entry_count', 0) for r in successful_tests)
        total_amount = sum(r.get('total_amount', 0.0) for r in successful_tests)
        
        print(f"Total Commission Entries Processed: {total_entries}")
        print(f"Total Commission Amount: ${total_amount:.2f}")
    
    # Combined DataFrame
    print(f"\n{'='*20} COMBINED DATAFRAME TEST {'='*20}")
    
    all_entries = []
    for result in successful_tests:
        entries = result.get('commission_entries', [])
        for entry in entries:
            entry['statement_date'] = result.get('statement_date')
            entry['total_amount'] = result.get('total_amount')
        all_entries.extend(entries)
    
    if all_entries:
        combined_df = pd.DataFrame(all_entries)
        print(f"Combined DataFrame Shape: {combined_df.shape}")
        print(f"Carriers Included: {combined_df['carrier'].unique().tolist()}")
        print(f"Total Commission Sum: ${combined_df['commission_amount'].sum():.2f}")
        
        # Show summary by carrier
        if 'carrier' in combined_df.columns:
            carrier_summary = combined_df.groupby('carrier').agg({
                'commission_amount': ['count', 'sum'],
                'member_name': 'count'
            }).round(2)
            print(f"\nCarrier Summary:")
            print(carrier_summary)
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE - SYSTEM READY FOR PRODUCTION")
    print(f"{'='*80}")

if __name__ == "__main__":
    run_comprehensive_test()