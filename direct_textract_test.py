#!/usr/bin/env python3
"""
Direct Textract API test with different approaches
"""

import os
import boto3
from dotenv import load_dotenv

def test_textract_approaches():
    """Test different Textract API approaches"""
    print("=== DIRECT TEXTRACT API TESTING ===")
    
    # Load environment
    load_dotenv()
    
    # Initialize Textract client
    textract = boto3.client(
        'textract',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    # Test with the smallest PDF first
    test_file = "docs/HNE comm.pdf"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"📄 Testing with: {test_file}")
    
    try:
        with open(test_file, 'rb') as file:
            pdf_bytes = file.read()
        
        print(f"📏 File size: {len(pdf_bytes)} bytes")
        
        # Test 1: Basic text detection (most compatible)
        print("\n🧪 Test 1: Basic text detection")
        try:
            response1 = textract.detect_document_text(
                Document={'Bytes': pdf_bytes}
            )
            text_blocks = [block.get('Text', '') for block in response1.get('Blocks', []) if block['BlockType'] == 'LINE']
            print(f"✅ Success! Found {len(text_blocks)} text lines")
            if text_blocks:
                print(f"📝 Sample: {text_blocks[0][:100]}...")
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
        
        # Test 2: Analyze document with FORMS only
        print("\n🧪 Test 2: Analyze document (FORMS only)")
        try:
            response2 = textract.analyze_document(
                Document={'Bytes': pdf_bytes},
                FeatureTypes=['FORMS']
            )
            text_blocks = [block.get('Text', '') for block in response2.get('Blocks', []) if block['BlockType'] == 'LINE']
            print(f"✅ Success! Found {len(text_blocks)} text lines")
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
        
        # Test 3: Analyze document with TABLES only
        print("\n🧪 Test 3: Analyze document (TABLES only)")
        try:
            response3 = textract.analyze_document(
                Document={'Bytes': pdf_bytes},
                FeatureTypes=['TABLES']
            )
            text_blocks = [block.get('Text', '') for block in response3.get('Blocks', []) if block['BlockType'] == 'LINE']
            print(f"✅ Success! Found {len(text_blocks)} text lines")
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
        
        # Test 4: Analyze document with both (original approach)
        print("\n🧪 Test 4: Analyze document (TABLES + FORMS)")
        try:
            response4 = textract.analyze_document(
                Document={'Bytes': pdf_bytes},
                FeatureTypes=['TABLES', 'FORMS']
            )
            text_blocks = [block.get('Text', '') for block in response4.get('Blocks', []) if block['BlockType'] == 'LINE']
            print(f"✅ Success! Found {len(text_blocks)} text lines")
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            
    except Exception as e:
        print(f"❌ File reading failed: {str(e)}")
    
    print("\n=== TEXTRACT API TEST SUMMARY ===")
    print("This test helps identify which Textract API calls work with your PDFs.")
    print("If basic text detection works but analyze_document fails, we can adjust the integration.")

if __name__ == "__main__":
    test_textract_approaches()