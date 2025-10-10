#!/usr/bin/env python3
"""
Comprehensive Textract test matching the service exactly
"""

import os
import boto3
from dotenv import load_dotenv

def test_exact_textract_workflow():
    """Test the exact same workflow as the TextractExtractionService"""
    print("=== EXACT TEXTRACT WORKFLOW TEST ===")
    
    load_dotenv()
    
    # Initialize Textract client exactly like the service
    textract_client = boto3.client(
        'textract',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    test_file = "docs/HNE comm.pdf"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"📄 Testing exact workflow with: {test_file}")
    
    try:
        # Step 1: Read file exactly like the service
        with open(test_file, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
        
        print(f"✅ Step 1: File read successfully ({len(pdf_bytes)} bytes)")
        
        # Step 2: Call analyze_document exactly like the service
        response = textract_client.analyze_document(
            Document={'Bytes': pdf_bytes},
            FeatureTypes=['TABLES', 'FORMS']
        )
        
        print(f"✅ Step 2: analyze_document call successful")
        print(f"   📊 Blocks found: {len(response.get('Blocks', []))}")
        
        # Step 3: Extract text like the service does
        text_lines = []
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                text_lines.append(block.get('Text', ''))
        
        text_content = '\n'.join(text_lines)
        print(f"✅ Step 3: Text extraction successful")
        print(f"   📝 Text lines: {len(text_lines)}")
        print(f"   📝 Sample: {text_content[:200]}...")
        
        # Step 4: Extract tables like the service does
        # Create a map of block IDs to blocks
        block_map = {block['Id']: block for block in response.get('Blocks', [])}
        
        # Find TABLE blocks
        table_blocks = [block for block in response.get('Blocks', []) if block['BlockType'] == 'TABLE']
        print(f"✅ Step 4: Found {len(table_blocks)} tables")
        
        tables = []
        for table_block in table_blocks:
            # Extract table structure
            table_data = []
            if 'Relationships' in table_block:
                for relationship in table_block['Relationships']:
                    if relationship['Type'] == 'CHILD':
                        cell_blocks = [block_map[cell_id] for cell_id in relationship['Ids'] 
                                     if cell_id in block_map]
                        
                        # Group cells by row
                        rows = {}
                        for cell in cell_blocks:
                            row_index = cell.get('RowIndex', 0)
                            col_index = cell.get('ColumnIndex', 0)
                            
                            if row_index not in rows:
                                rows[row_index] = {}
                            
                            # Extract cell text
                            cell_text = ""
                            if 'Relationships' in cell:
                                for cell_rel in cell['Relationships']:
                                    if cell_rel['Type'] == 'CHILD':
                                        word_blocks = [block_map[word_id] for word_id in cell_rel['Ids'] 
                                                     if word_id in block_map and block_map[word_id]['BlockType'] == 'WORD']
                                        cell_text = ' '.join([word.get('Text', '') for word in word_blocks])
                            
                            rows[row_index][col_index] = cell_text
                        
                        # Convert to list of lists
                        max_row = max(rows.keys()) if rows else 0
                        for row_idx in range(1, max_row + 1):
                            row_data = []
                            if row_idx in rows:
                                max_col = max(rows[row_idx].keys()) if rows[row_idx] else 0
                                for col_idx in range(1, max_col + 1):
                                    row_data.append(rows[row_idx].get(col_idx, ''))
                            table_data.append(row_data)
            
            if table_data:
                tables.append(table_data)
                print(f"   📊 Table with {len(table_data)} rows extracted")
                if table_data:
                    print(f"   📊 First row: {table_data[0]}")
        
        # Step 5: Check what would happen for HNE processing
        print(f"\n🔍 HNE Processing Analysis:")
        print(f"   📊 Tables available for processing: {len(tables)}")
        
        # Check for statement date in text (HNE pattern)
        import re
        hne_date_pattern = r'(\d{1,2}/\d{1,2}/20\d{2})'
        dates_found = re.findall(hne_date_pattern, text_content)
        print(f"   📅 HNE date patterns found: {dates_found}")
        
        if tables:
            print(f"   ✅ Tables found - commission entries should be extractable")
        else:
            print(f"   ❌ No tables found - this explains why no entries are extracted")
            
    except Exception as e:
        print(f"❌ Error in workflow: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_exact_textract_workflow()