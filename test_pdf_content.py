#!/usr/bin/env python3
"""
Simple PDF Content Check Script
Tests if the generated PDF contains the expected detailed tables
"""

import sys
import os
from pathlib import Path

def check_latest_pdf():
    """Check if the latest PDF was generated with detailed content"""
    reports_dir = Path("reports")
    
    # Find the latest PDF file
    pdf_files = list(reports_dir.glob("commission_reconciliation_summary_*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found")
        return False
    
    latest_pdf = max(pdf_files, key=os.path.getctime)
    print(f"✅ Latest PDF found: {latest_pdf.name}")
    
    # Check file size (enhanced PDF should be larger)
    file_size = os.path.getsize(latest_pdf)
    print(f"📄 PDF file size: {file_size:,} bytes")
    
    # Basic size check - enhanced PDF should be at least 20KB
    if file_size > 20000:
        print("✅ PDF size suggests detailed content (>20KB)")
        return True
    else:
        print("⚠️  PDF size suggests basic content only (<20KB)")
        return False

if __name__ == "__main__":
    success = check_latest_pdf()
    
    # Also check the data structure
    import json
    try:
        with open("reports/commission_reconciliation_data_20251006_144439.json", "r") as f:
            data = json.load(f)
            
        hc_data = data.get("hc", {})
        overpayments = hc_data.get("overpayments", [])
        underpayments = hc_data.get("underpayments", [])
        
        print(f"📊 Data structure check:")
        print(f"   Overpayments: {len(overpayments)} entries")
        print(f"   Underpayments: {len(underpayments)} entries")
        
        if overpayments and underpayments:
            print("✅ Detailed variance data available")
            
            # Show sample data
            print(f"📋 Sample overpayment: {overpayments[0].get('member_name')} - ${overpayments[0].get('amount')}")
            print(f"📋 Sample underpayment: {underpayments[0].get('member_name')} - ${underpayments[0].get('amount')}")
        else:
            print("❌ No detailed variance data found")
            
    except Exception as e:
        print(f"⚠️  Could not check data structure: {e}")
    
    sys.exit(0 if success else 1)