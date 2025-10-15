"""
Test script for Enhanced LandingAI Extraction Service
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from enhanced_landingai_service_fixed import EnhancedLandingAIExtractionService

def test_enhanced_extraction():
    """Test the enhanced extraction service"""
    
    service = EnhancedLandingAIExtractionService()
    
    if not service.is_available():
        print("Enhanced LandingAI service not available")
        return
    
    print("Testing Enhanced LandingAI Extraction...")
    
    test_files = [
        ("docs/HC_COMMISSION_1462-001_R.pdf", "hc"),
        ("docs/HNE comm.pdf", "hne"),
        ("docs/Humana_commission_statement_jul.pdf", "humana")
    ]
    
    for pdf_path, carrier in test_files:
        if os.path.exists(pdf_path):
            print(f"\nTesting: {pdf_path}")
            result = service.extract_commission_data_enhanced(pdf_path, carrier)
            
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Success: {result['entry_count']} entries, ${result['total_amount']}")
                print(f"   Carrier: {result['carrier']}")
                print(f"   Date: {result['statement_date']}")
                
                for i, entry in enumerate(result['commission_entries'][:3]):  # Show first 3
                    print(f"   Entry {i+1}: {entry['policy_id']} - ${entry['commission_amount']}")

if __name__ == "__main__":
    test_enhanced_extraction()
