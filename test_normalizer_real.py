"""
Test normalizer with actual LandingAI data
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from landingai_extract_normalizer import LandingAIExtractNormalizer

def test_normalizer_with_real_data():
    """Test normalizer with actual LandingAI JSON output"""
    
    print("="*60)
    print("TESTING NORMALIZER WITH REAL LANDINGAI DATA")
    print("="*60)
    
    # Load the actual extraction data
    with open('hc_extraction_debug.json', 'r', encoding='utf-8') as f:
        real_data = json.load(f)
    
    print(f"Loaded data with {len(real_data.get('chunks', []))} chunks")
    print(f"Markdown length: {len(real_data.get('markdown', ''))}")
    
    # Initialize normalizer
    normalizer = LandingAIExtractNormalizer()
    
    # Test normalization
    result = normalizer.normalize_extract(real_data)
    
    print(f"\nNormalizer Results:")
    print(f"  Carrier: {result.get('carrier')}")
    print(f"  Statement Date: {result.get('statement_date')}")
    print(f"  Total Amount: ${result.get('total_amount', 0.0):.2f}")
    print(f"  Entry Count: {result.get('entry_count', 0)}")
    print(f"  Agent Info: {result.get('agent_info', {})}")
    
    entries = result.get('commission_entries', [])
    if entries:
        print(f"\nCommission Entries:")
        for i, entry in enumerate(entries):
            print(f"  {i+1}. {entry.get('member_name', 'Unknown')} - "
                  f"${entry.get('commission_amount', 0.0):.2f} - "
                  f"Policy: {entry.get('policy_id', 'Unknown')}")
    else:
        print(f"\n❌ No commission entries found!")
        
        # Debug: let's look at the markdown content
        markdown = result.get('markdown', real_data.get('markdown', ''))
        print(f"\nDebugging markdown content...")
        print(f"Looking for table patterns...")
        
        if '<table' in markdown:
            print("✅ Found HTML tables")
            import re
            tables = re.findall(r'<table[^>]*>(.*?)</table>', markdown, re.DOTALL)
            print(f"Number of tables: {len(tables)}")
            
            for i, table in enumerate(tables):
                rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL)
                print(f"\nTable {i+1}: {len(rows)} rows")
                
                # Show all rows for debugging
                for j, row in enumerate(rows[:5]):  # Show first 5 rows
                    cells = re.findall(r'<td[^>]*[^>]*>(.*?)</td>', row, re.DOTALL)
                    cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                    print(f"  Row {j+1}: {cells}")
        else:
            print("❌ No HTML tables found")
            print("Looking for table-like patterns...")
            
            # Look for pipe-separated tables
            lines = markdown.split('\n')
            for i, line in enumerate(lines):
                if '|' in line and len(line.split('|')) > 3:
                    print(f"Line {i}: {line}")
    
    # Save normalized result for inspection
    with open('normalized_debug.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\nNormalized result saved to: normalized_debug.json")

if __name__ == "__main__":
    test_normalizer_with_real_data()