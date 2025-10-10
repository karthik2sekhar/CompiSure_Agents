#!/usr/bin/env python3
"""
Test script for LandingAI ADE extraction integration
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.landingai_extraction_service import LandingAIExtractionService
from src.commission_processor import CommissionProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_landingai_extraction():
    """Test LandingAI extraction service"""
    
    logger.info("=== LANDINGAI ADE EXTRACTION TEST ===")
    
    # Initialize service
    service = LandingAIExtractionService()
    
    # Check availability
    if not service.is_available():
        logger.warning("❌ LandingAI service not available")
        logger.info("Reasons:")
        logger.info("  - VISION_AGENT_API_KEY not configured")
        logger.info("  - landingai-ade package not installed")
        return False
    
    logger.info("✅ LandingAI service initialized successfully")
    
    # Test with sample PDFs
    docs_dir = Path("docs")
    if not docs_dir.exists():
        logger.warning("❌ No docs directory found")
        return False
    
    pdf_files = list(docs_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning("❌ No PDF files found in docs directory")
        return False
    
    logger.info(f"📄 Found {len(pdf_files)} PDF files to test")
    
    # Test extraction on first PDF
    test_pdf = pdf_files[0]
    logger.info(f"🔍 Testing extraction on: {test_pdf.name}")
    
    try:
        result = service.extract_commission_data(str(test_pdf))
        
        if result and 'error' not in result:
            logger.info("✅ LandingAI extraction successful!")
            logger.info(f"  - Carrier: {result.get('carrier', 'unknown')}")
            logger.info(f"  - Statement Date: {result.get('statement_date', 'not found')}")
            logger.info(f"  - Agent Info: {result.get('agent_info', {})}")
            logger.info(f"  - Total Amount: ${result.get('total_amount', 0)}")
            logger.info(f"  - Commission Entries: {len(result.get('commission_entries', []))}")
            
            # Test DataFrame conversion
            df = service.to_dataframe(result)
            if not df.empty:
                logger.info(f"✅ DataFrame conversion successful: {len(df)} rows")
            else:
                logger.warning("⚠️ DataFrame conversion resulted in empty DataFrame")
            
            return True
        else:
            logger.error(f"❌ LandingAI extraction failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {str(e)}")
        return False

def test_commission_processor_integration():
    """Test LandingAI integration with CommissionProcessor"""
    
    logger.info("=== COMMISSION PROCESSOR INTEGRATION TEST ===")
    
    # Initialize processor
    processor = CommissionProcessor()
    
    logger.info(f"✅ CommissionProcessor initialized")
    logger.info(f"  - LandingAI enabled: {processor.use_landingai}")
    
    if not processor.use_landingai:
        logger.warning("❌ LandingAI integration not enabled")
        logger.info("To enable:")
        logger.info("  1. Set VISION_AGENT_API_KEY in .env file")
        logger.info("  2. Set USE_LANDING_AI=true in .env file")
        return False
    
    # Test processing
    docs_dir = "docs"
    if os.path.exists(docs_dir):
        logger.info(f"🔍 Testing commission processing with LandingAI...")
        results = processor.process_all_statements(docs_dir)
        
        if results:
            logger.info("✅ Commission processing with LandingAI successful!")
            for carrier, data in results.items():
                if isinstance(data, list):
                    logger.info(f"  - {carrier}: {len(data)} commission entries")
                else:
                    logger.info(f"  - {carrier}: {data.get('extraction_method', 'unknown')} extraction")
            return True
        else:
            logger.warning("⚠️ No results from commission processing")
            return False
    else:
        logger.warning("❌ No docs directory found for testing")
        return False

def main():
    """Main test function"""
    
    logger.info("🚀 Starting LandingAI ADE Integration Tests")
    
    # Test 1: LandingAI service
    service_test = test_landingai_extraction()
    
    # Test 2: Commission processor integration
    integration_test = test_commission_processor_integration()
    
    # Summary
    logger.info("=== TEST SUMMARY ===")
    logger.info(f"LandingAI Service Test: {'✅ PASSED' if service_test else '❌ FAILED'}")
    logger.info(f"Integration Test: {'✅ PASSED' if integration_test else '❌ FAILED'}")
    
    if service_test and integration_test:
        logger.info("🎉 ALL TESTS PASSED - LandingAI ADE integration ready!")
        return True
    else:
        logger.warning("⚠️ Some tests failed - check configuration and API keys")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)