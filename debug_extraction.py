"""
Debug script to examine LandingAI JSON output and identify parsing issues
"""

import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from landingai_extract_normalizer import LandingAIExtractNormalizer
from src.landingai_extraction_service import LandingAIExtractionService

def debug_landingai_extraction():
    """Debug the LandingAI extraction for HC document"""
    
    print("="*60)
    print("LANDINGAI EXTRACTION DEBUG")
    print("="*60)
    
    # Initialize services
    landingai_service = LandingAIExtractionService()
    normalizer = LandingAIExtractNormalizer()
    
    # Test HC document
    hc_file = "docs/HC_COMMISSION_1462-001_R.pdf"
    
    if not os.path.exists(hc_file):
        print(f"File not found: {hc_file}")
        return
    
    print(f"Processing: {hc_file}")
    
    try:
        # Get raw LandingAI response
        print("\n1. Getting raw LandingAI response...")
        raw_response = landingai_service.client.parse(
            document=hc_file,
            model="dpt-2-latest"
        )
        
        # Convert to dict
        if hasattr(raw_response, 'dict'):
            raw_data = raw_response.dict()
        elif hasattr(raw_response, 'model_dump'):
            raw_data = raw_response.model_dump()
        else:
            raw_data = raw_response
        
        # Save raw data for inspection
        with open('debug_hc_raw.json', 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=2, default=str)
        
        print(f"Raw data saved to: debug_hc_raw.json")
        print(f"Markdown length: {len(raw_data.get('markdown', ''))}")
        print(f"Chunks count: {len(raw_data.get('chunks', []))}")
        
        # Show first 500 chars of markdown
        markdown = raw_data.get('markdown', '')
        print(f"\nFirst 500 chars of markdown:")
        print("-" * 40)
        print(markdown[:500])
        print("-" * 40)
        
        # Show chunk types
        chunks = raw_data.get('chunks', [])
        print(f"\nChunk types:")
        for i, chunk in enumerate(chunks):
            chunk_type = chunk.get('type', 'unknown')
            chunk_text = chunk.get('markdown', '')[:100]
            print(f"  {i}: {chunk_type} - {len(chunk_text)} chars - {chunk_text[:50]}...")
        
        # Test our normalizer
        print(f"\n2. Testing our normalizer...")
        normalized_result = normalizer.normalize_extract(raw_data)
        
        print(f"Normalizer results:")
        print(f"  Carrier: {normalized_result.get('carrier')}")
        print(f"  Statement Date: {normalized_result.get('statement_date')}")
        print(f"  Total Amount: ${normalized_result.get('total_amount', 0.0):.2f}")
        print(f"  Entry Count: {normalized_result.get('entry_count', 0)}")
        
        entries = normalized_result.get('commission_entries', [])
        if entries:
            print(f"  Sample entries:")
            for i, entry in enumerate(entries[:3]):
                print(f"    {i+1}: {entry.get('member_name', 'Unknown')} - ${entry.get('commission_amount', 0.0):.2f}")
        else:
            print(f"  No entries found!")
            
        # Look for table patterns
        print(f"\n3. Looking for table patterns in markdown...")
        if '<table' in markdown:
            print("  Found HTML tables in markdown")
            import re
            tables = re.findall(r'<table[^>]*>(.*?)</table>', markdown, re.DOTALL)
            print(f"  Number of tables: {len(tables)}")
            
            for i, table in enumerate(tables):
                rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL)
                print(f"    Table {i+1}: {len(rows)} rows")
                if rows:
                    # Show first row
                    cells = re.findall(r'<td[^>]*[^>]*>(.*?)</td>', rows[0], re.DOTALL)
                    cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                    print(f"      First row: {cells}")
        
        # Look for dollar amounts
        print(f"\n4. Looking for dollar amounts...")
        import re
        amounts = re.findall(r'\$[\d,]+\.?\d*', markdown)
        print(f"  Found amounts: {amounts}")
        
        # Look for commission-related patterns
        commission_patterns = [
            r'commission[^$]*\$?([\d,]+\.?\d*)',
            r'total[^$]*\$?([\d,]+\.?\d*)',
            r'amount[^$]*\$?([\d,]+\.?\d*)'
        ]
        
        for pattern in commission_patterns:
            matches = re.findall(pattern, markdown, re.IGNORECASE)
            if matches:
                print(f"  Pattern '{pattern}': {matches}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_landingai_extraction()