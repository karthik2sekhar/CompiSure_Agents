#!/usr/bin/env python3
"""
Test what the Textract service actually returns
"""

import os
import json
from dotenv import load_dotenv
from src.textract_service import TextractExtractionService

def test_textract_service_output():
    """Test what the Textract service returns for each PDF"""
    print("=== TEXTRACT SERVICE OUTPUT TEST ===")
    
    load_dotenv()
    
    # Initialize Textract service
    textract_service = TextractExtractionService()
    
    pdf_files = [
        ("docs/HNE comm.pdf", "hne"),
        ("docs/HC_COMMISSION_1462-001_R.pdf", "hc"),
        ("docs/Humana_commission_statement_jul.pdf", "humana")
    ]
    
    for pdf_path, carrier in pdf_files:
        if not os.path.exists(pdf_path):
            print(f"❌ File not found: {pdf_path}")
            continue
            
        print(f"\n📄 Testing {carrier.upper()}: {os.path.basename(pdf_path)}")
        
        try:
            result = textract_service.extract_from_pdf(pdf_path, carrier)
            
            if result:
                print(f"✅ Textract extraction successful!")
                print(f"   📊 Keys in result: {list(result.keys())}")
                
                entries = result.get('entries', [])
                print(f"   📋 Number of entries: {len(entries)}")
                
                if entries:
                    print(f"   📝 Sample entry: {entries[0]}")
                    print(f"   💰 Total entries with amounts: {sum(1 for e in entries if e.get('amount'))}")
                else:
                    print(f"   ⚠️  No entries found in result")
                    
                tables = result.get('tables', [])
                print(f"   📊 Number of tables: {len(tables)}")
                
                key_value_pairs = result.get('key_value_pairs', [])
                print(f"   🔑 Number of key-value pairs: {len(key_value_pairs)}")
                
                statement_date = result.get('statement_date')
                print(f"   📅 Statement date: {statement_date}")
                
            else:
                print(f"❌ Textract extraction returned None")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n=== DIAGNOSIS ===")
    print("This test shows exactly what data Textract is extracting from each PDF.")
    print("If entries = 0, it means the table extraction isn't finding commission data.")

if __name__ == "__main__":
    test_textract_service_output()