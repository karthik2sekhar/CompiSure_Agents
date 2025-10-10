#!/usr/bin/env python3
"""
Debug table structure and column detection
"""

import os
from dotenv import load_dotenv
from src.textract_service import TextractExtractionService

def debug_table_structure():
    """Debug the table structure and column detection"""
    print("=== TABLE STRUCTURE DEBUGGING ===")
    
    load_dotenv()
    
    # Initialize service
    service = TextractExtractionService()
    
    # Test directly on the table extraction
    import boto3
    textract_client = boto3.client(
        'textract',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    test_file = "docs/HNE comm.pdf"
    
    with open(test_file, 'rb') as pdf_file:
        pdf_bytes = pdf_file.read()
    
    response = textract_client.analyze_document(
        Document={'Bytes': pdf_bytes},
        FeatureTypes=['TABLES', 'FORMS']
    )
    
    # Extract tables using the service method
    tables = service._extract_tables(response)
    
    print(f"📊 Found {len(tables)} tables")
    
    for i, table in enumerate(tables):
        print(f"\n📋 Table {i+1}:")
        print(f"   Rows: {len(table)}")
        if table:
            print(f"   Columns: {len(table[0])}")
            print(f"   Headers: {table[0]}")
            
            if len(table) > 1:
                print(f"   First data row: {table[1]}")
                
            # Test column detection like HNE does
            header_row = table[0]
            policy_col = None
            amount_col = None
            
            for j, header in enumerate(header_row):
                header_lower = header.lower()
                if any(keyword in header_lower for keyword in ['contract id', 'policy', 'certificate', 'member id']):
                    policy_col = j
                    print(f"   🎯 Policy column found at index {j}: '{header}'")
                elif any(keyword in header_lower for keyword in ['payout amt', 'amount', 'commission', '$', 'rate']):
                    amount_col = j
                    print(f"   💰 Amount column found at index {j}: '{header}'")
            
            if policy_col is None:
                print("   ❌ No policy column detected")
            if amount_col is None:
                print("   ❌ No amount column detected")
                
            # Show a few data rows for context
            if len(table) > 1:
                print(f"   📄 Sample data rows:")
                for row_idx in range(1, min(4, len(table))):
                    print(f"      Row {row_idx}: {table[row_idx]}")

if __name__ == "__main__":
    debug_table_structure()