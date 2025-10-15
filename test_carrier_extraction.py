#!/usr/bin/env python3
"""
Comprehensive LandingAI Carrier Testing
Tests LandingAI extraction for each carrier and compares with fallback methods
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.landingai_extraction_service import LandingAIExtractionService
from src.commission_processor import CommissionProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_carrier_extraction():
    """Test LandingAI extraction for each carrier"""
    
    logger.info("🚀 COMPREHENSIVE CARRIER EXTRACTION TEST")
    logger.info("=" * 60)
    
    # Initialize services
    landingai_service = LandingAIExtractionService()
    processor = CommissionProcessor()
    
    # Check service availability
    logger.info("📋 Service Status:")
    logger.info(f"  - LandingAI Available: {landingai_service.is_available()}")
    logger.info(f"  - LandingAI Enabled in Processor: {processor.use_landingai}")
    logger.info(f"  - API Key Configured: {'Yes' if os.environ.get('VISION_AGENT_API_KEY') else 'No'}")
    logger.info("")
    
    if not landingai_service.is_available():
        logger.error("❌ LandingAI service not available - cannot run carrier tests")
        return False
    
    # Find all PDFs in docs directory
    docs_dir = Path("docs")
    if not docs_dir.exists():
        logger.error("❌ No docs directory found")
        return False
    
    pdf_files = list(docs_dir.glob("*.pdf"))
    if not pdf_files:
        logger.error("❌ No PDF files found in docs directory")
        return False
    
    logger.info(f"📄 Found {len(pdf_files)} PDF files to test:")
    for pdf in pdf_files:
        logger.info(f"  - {pdf.name}")
    logger.info("")
    
    # Test each carrier
    results = {}
    
    for pdf_file in pdf_files:
        logger.info(f"🔍 TESTING: {pdf_file.name}")
        logger.info("-" * 40)
        
        # Detect carrier from filename
        carrier = detect_carrier_from_filename(pdf_file.name)
        logger.info(f"Detected Carrier: {carrier.upper() if carrier else 'UNKNOWN'}")
        
        # Test LandingAI extraction
        try:
            logger.info("Testing LandingAI extraction...")
            landingai_result = landingai_service.extract_commission_data(str(pdf_file), carrier)
            
            if landingai_result and 'error' not in landingai_result:
                logger.info("✅ LandingAI extraction SUCCESSFUL")
                logger.info(f"  📊 Results:")
                logger.info(f"    - Carrier: {landingai_result.get('carrier', 'unknown')}")
                logger.info(f"    - Statement Date: {landingai_result.get('statement_date', 'not found')}")
                logger.info(f"    - Commission Entries: {len(landingai_result.get('commission_entries', []))}")
                logger.info(f"    - Total Amount: ${landingai_result.get('total_amount', 0)}")
                logger.info(f"    - Agent Info: {landingai_result.get('agent_info', {})}")
                
                # Convert to DataFrame
                df = landingai_service.to_dataframe(landingai_result)
                if not df.empty:
                    logger.info(f"    - DataFrame: {len(df)} rows created")
                    logger.info(f"    - Columns: {list(df.columns)}")
                
                results[pdf_file.name] = {
                    'carrier': carrier,
                    'landingai_success': True,
                    'landingai_result': landingai_result,
                    'error': None
                }
                
            else:
                error_msg = landingai_result.get('error', 'Unknown error') if landingai_result else 'No result returned'
                logger.error(f"❌ LandingAI extraction FAILED: {error_msg}")
                results[pdf_file.name] = {
                    'carrier': carrier,
                    'landingai_success': False,
                    'landingai_result': None,
                    'error': error_msg
                }
                
        except Exception as e:
            logger.error(f"❌ LandingAI extraction EXCEPTION: {str(e)}")
            results[pdf_file.name] = {
                'carrier': carrier,
                'landingai_success': False,
                'landingai_result': None,
                'error': str(e)
            }
        
        logger.info("")
    
    # Summary report
    logger.info("📈 EXTRACTION SUMMARY BY CARRIER")
    logger.info("=" * 60)
    
    carrier_summary = {}
    for filename, result in results.items():
        carrier = result['carrier'] or 'unknown'
        if carrier not in carrier_summary:
            carrier_summary[carrier] = {'total': 0, 'successful': 0, 'failed': 0, 'files': []}
        
        carrier_summary[carrier]['total'] += 1
        carrier_summary[carrier]['files'].append(filename)
        
        if result['landingai_success']:
            carrier_summary[carrier]['successful'] += 1
        else:
            carrier_summary[carrier]['failed'] += 1
    
    for carrier, stats in carrier_summary.items():
        logger.info(f"\n🏢 {carrier.upper()}:")
        logger.info(f"  📄 Files: {stats['total']}")
        logger.info(f"  ✅ Successful: {stats['successful']}")
        logger.info(f"  ❌ Failed: {stats['failed']}")
        logger.info(f"  📋 Success Rate: {(stats['successful']/stats['total']*100):.1f}%")
        
        # Show detailed results for successful extractions
        for filename in stats['files']:
            file_result = results[filename]
            if file_result['landingai_success']:
                landingai_data = file_result['landingai_result']
                entries = len(landingai_data.get('commission_entries', []))
                amount = landingai_data.get('total_amount', 0)
                date = landingai_data.get('statement_date', 'N/A')
                logger.info(f"    📊 {filename}: {entries} entries, ${amount}, date: {date}")
            else:
                logger.info(f"    ❌ {filename}: {file_result['error']}")
    
    # Overall statistics
    total_files = len(results)
    successful_files = sum(1 for r in results.values() if r['landingai_success'])
    
    logger.info(f"\n🎯 OVERALL RESULTS:")
    logger.info(f"  📄 Total Files Tested: {total_files}")
    logger.info(f"  ✅ Successful Extractions: {successful_files}")
    logger.info(f"  ❌ Failed Extractions: {total_files - successful_files}")
    logger.info(f"  📊 Overall Success Rate: {(successful_files/total_files*100):.1f}%")
    
    return successful_files == total_files

def test_integrated_processing():
    """Test the integrated commission processing with LandingAI"""
    
    logger.info("\n🔄 INTEGRATED COMMISSION PROCESSING TEST")
    logger.info("=" * 60)
    
    processor = CommissionProcessor()
    
    logger.info("Processing all statements with LandingAI integration...")
    
    try:
        results = processor.process_all_statements("docs")
        
        if results:
            logger.info("✅ Integrated processing SUCCESSFUL")
            logger.info("\n📊 Processing Results:")
            
            total_entries = 0
            total_amount = 0.0
            
            for carrier, data in results.items():
                if isinstance(data, dict):
                    entries = len(data.get('commission_entries', []))
                    amount = data.get('total_amount', 0)
                    method = data.get('extraction_method', 'unknown')
                    date = data.get('statement_date', 'N/A')
                    
                    logger.info(f"  🏢 {carrier.upper()}:")
                    logger.info(f"    - Entries: {entries}")
                    logger.info(f"    - Amount: ${amount}")
                    logger.info(f"    - Method: {method}")
                    logger.info(f"    - Date: {date}")
                    
                    total_entries += entries
                    total_amount += amount
                    
                elif isinstance(data, list):
                    logger.info(f"  🏢 {carrier.upper()}: {len(data)} entries (legacy format)")
                    total_entries += len(data)
            
            logger.info(f"\n🎯 TOTALS:")
            logger.info(f"  📊 Total Entries: {total_entries}")
            logger.info(f"  💰 Total Amount: ${total_amount}")
            
            return True
        else:
            logger.error("❌ Integrated processing returned no results")
            return False
            
    except Exception as e:
        logger.error(f"❌ Integrated processing FAILED: {str(e)}")
        return False

def detect_carrier_from_filename(filename):
    """Detect carrier from filename"""
    filename_lower = filename.lower()
    
    if 'humana' in filename_lower:
        return 'humana'
    elif 'hc_commission' in filename_lower or filename_lower.startswith('hc_'):
        return 'hc'
    elif 'hne' in filename_lower:
        return 'hne'
    elif 'blue_cross' in filename_lower or 'bluecross' in filename_lower:
        return 'blue_cross'
    elif 'aetna' in filename_lower:
        return 'aetna'
    elif 'cigna' in filename_lower:
        return 'cigna'
    elif 'unitedhealth' in filename_lower or 'united' in filename_lower:
        return 'unitedhealth'
    
    return None

def main():
    """Main test function"""
    
    print("🚀 LandingAI Carrier Extraction Testing Suite")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test 1: Individual carrier extraction
    carrier_test_passed = test_carrier_extraction()
    
    # Test 2: Integrated processing
    integration_test_passed = test_integrated_processing()
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("🏁 FINAL TEST RESULTS")
    logger.info("=" * 80)
    logger.info(f"✅ Carrier Extraction Tests: {'PASSED' if carrier_test_passed else 'FAILED'}")
    logger.info(f"✅ Integration Tests: {'PASSED' if integration_test_passed else 'FAILED'}")
    
    if carrier_test_passed and integration_test_passed:
        logger.info("🎉 ALL TESTS PASSED - LandingAI is working perfectly!")
        logger.info("💡 Your commission processing system is now using advanced AI extraction")
    else:
        logger.warning("⚠️ Some tests failed - check logs above for details")
    
    logger.info(f"🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return carrier_test_passed and integration_test_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)