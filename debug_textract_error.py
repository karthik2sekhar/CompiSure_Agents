#!/usr/bin/env python3
"""
Debug the exact line where the error occurs in TextractExtractionService
"""

import os
import traceback
from dotenv import load_dotenv
from src.textract_service import TextractExtractionService

def debug_textract_service():
    """Debug the TextractExtractionService step by step"""
    print("=== TEXTRACT SERVICE DEBUGGING ===")
    
    load_dotenv()
    
    # Initialize service
    textract_service = TextractExtractionService()
    
    test_file = "docs/HNE comm.pdf"
    carrier = "hne"
    
    print(f"📄 Debugging: {test_file}")
    
    try:
        result = textract_service.extract_from_pdf(test_file, carrier)
        print(f"✅ Success: {result}")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_textract_service()