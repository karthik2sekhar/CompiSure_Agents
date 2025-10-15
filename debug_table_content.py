import json
import os
import re

def debug_table_content():
    """Debug table content to understand why only 1 table is detected"""
    
    # Load Humana JSON response
    response_dir = "landingai_system_responses"
    humana_files = [f for f in os.listdir(response_dir) if f.startswith('Humana_')]
    
    if not humana_files:
        print("❌ No Humana files found")
        return
    
    with open(os.path.join(response_dir, humana_files[0]), 'r') as f:
        response_data = json.load(f)
    
    chunks = response_data['chunks']
    print(f"📄 Total chunks: {len(chunks)}")
    
    # Find all tables and check their content
    tables_found = []
    for i, chunk in enumerate(chunks):
        if chunk.get('type') == 'table':
            chunk_markdown = chunk.get('markdown', '')
            tables_found.append({
                'chunk_index': i,
                'contains_product_type': 'Product type' in chunk_markdown,
                'markdown_preview': chunk_markdown[:200] + '...' if len(chunk_markdown) > 200 else chunk_markdown
            })
    
    print(f"\n📊 All tables found: {len(tables_found)}")
    for i, table in enumerate(tables_found):
        print(f"\n   Table {i+1} at chunk {table['chunk_index']}:")
        print(f"   Contains 'Product type': {table['contains_product_type']}")
        print(f"   Content preview: {table['markdown_preview']}")

if __name__ == "__main__":
    debug_table_content()