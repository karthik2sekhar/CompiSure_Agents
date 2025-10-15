#!/usr/bin/env python3
"""
Debug script for Humana commission reconciliation
"""

import json
from commission_reconciliation_system import CommissionReconciliationSystem
import pandas as pd

def debug_humana_processing():
    """Debug the Humana extraction and matching process."""
    print("🔍 Debugging Humana Processing")
    print("=" * 50)
    
    # Initialize system
    system = CommissionReconciliationSystem()
    
    # Load enrollment data
    enrollment_df = system.load_enrollment_data()
    humana_enrollment = enrollment_df[enrollment_df['carrier'].str.lower() == 'humana'].copy()
    
    print(f"📊 Humana enrollment records: {len(humana_enrollment)}")
    for _, row in humana_enrollment.iterrows():
        print(f"   • {row['member_name']} ({row['policy_id']}) - Effective: {row['effective_date']}")
    
    # Process Humana JSON
    humana_file = "landingai_system_responses/Humana_commission_statement_jul_system_response_20251010_155456.json"
    commission_entries = system.extract_commission_data_generic(humana_file, 'humana')
    
    print(f"\n💰 Commission entries extracted: {len(commission_entries)}")
    for entry in commission_entries:
        print(f"   • Member: {entry['first_name']} {entry['last_name']} ({entry['member_id']})")
        print(f"     Effective Date: {entry['effective_date']}")
        print(f"     Month Paid: {entry.get('month_paid', 'N/A')}")
        print(f"     Amount: ${entry['net_amount']}")
        
        # Try to find matching enrollment
        for _, enroll_row in humana_enrollment.iterrows():
            if (enroll_row['policy_id'] == entry['member_id']):
                print(f"     🎯 Potential match found: {enroll_row['member_name']}")
                print(f"        Enrollment effective: {enroll_row['effective_date']}")
                print(f"        Commission effective: {entry['effective_date']}")
                
                # Check dates
                enroll_date = pd.to_datetime(enroll_row['effective_date'], errors='coerce')
                comm_date = pd.to_datetime(entry['effective_date'], errors='coerce') if entry['effective_date'] else None
                
                print(f"        Date match: {enroll_date == comm_date}")
        print()

if __name__ == "__main__":
    debug_humana_processing()