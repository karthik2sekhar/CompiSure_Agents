#!/usr/bin/env python3
"""
Simple Textract connectivity test
"""

import os
import logging
from dotenv import load_dotenv
from src.textract_service import TextractExtractionService

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_textract_connection():
    """Test basic Textract service connectivity"""
    print("=== TEXTRACT CONNECTIVITY TEST ===")
    
    # Load environment variables
    load_dotenv()
    
    # Check if AWS credentials are set
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION')
    use_textract = os.getenv('USE_TEXTRACT', 'false').lower() == 'true'
    
    print(f"AWS_ACCESS_KEY_ID: {'Set' if aws_access_key else 'Not set'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'Set' if aws_secret_key else 'Not set'}")
    print(f"AWS_REGION: {aws_region}")
    print(f"USE_TEXTRACT: {use_textract}")
    
    if not all([aws_access_key, aws_secret_key, aws_region]):
        print("❌ AWS credentials not properly configured!")
        return False
    
    if not use_textract:
        print("❌ USE_TEXTRACT is set to false!")
        return False
    
    try:
        # Initialize Textract service
        print("\n📡 Initializing Textract service...")
        textract_service = TextractExtractionService()
        print("✅ Textract service initialized successfully!")
        
        # Test with a sample PDF if available
        pdf_files = [f for f in os.listdir('docs') if f.endswith('.pdf')]
        if pdf_files:
            sample_pdf = os.path.join('docs', pdf_files[0])
            print(f"\n📄 Testing extraction with: {pdf_files[0]}")
            
            result = textract_service.extract_from_pdf(sample_pdf, 'hc')  # Test with HC carrier
            
            if result and 'success' in result and result['success']:
                print("✅ Textract extraction successful!")
                print(f"   - Tables found: {len(result.get('tables', []))}")
                print(f"   - Key-value pairs: {len(result.get('key_value_pairs', []))}")
                print(f"   - Commission entries: {len(result.get('commission_entries', []))}")
                return True
            else:
                print(f"❌ Textract extraction failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print("ℹ️  No PDF files found in docs/ directory for testing")
            print("✅ Textract service is properly configured and ready!")
            return True
            
    except Exception as e:
        print(f"❌ Textract initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_textract_connection()
    if success:
        print("\n🎉 TEXTRACT INTEGRATION IS WORKING!")
        print("Your AWS credentials are properly configured and Textract is ready to use.")
    else:
        print("\n💡 Please check your AWS credentials and configuration.")