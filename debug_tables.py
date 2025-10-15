#!/usr/bin/env python3
"""
Debug the exact table structure in Humana JSON
"""

import json
import re

def debug_tables():
    json_file = "landingai_system_responses/Humana_commission_statement_jul_system_response_20251010_155456.json"
    
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    chunks = json_data.get('chunks', [])
    print(f"📄 Total chunks: {len(chunks)}")
    
    # Find all members
    members = []
    for i, chunk in enumerate(chunks):
        chunk_markdown = chunk.get('markdown', '')
        member_match = re.search(r'([A-Z][a-zA-Z\'\s]+)\s+(\d{11}[A-Z])\s*\([^)]+\)\s*Effective\s+(\d{1,2}/\d{1,2}/\d{2,4})', chunk_markdown)
        if member_match:
            members.append({
                'chunk': i,
                'name': member_match.group(1).strip(),
                'id': member_match.group(2).strip()
            })
    
    print(f"\n👥 Members found: {len(members)}")
    for member in members:
        print(f"   Chunk {member['chunk']}: {member['name']} ({member['id']})")
    
    # Find all tables with Product type
    tables = []
    for i, chunk in enumerate(chunks):
        if chunk.get('type') == 'table' and 'Product type' in chunk.get('markdown', ''):
            # Extract table ID to identify unique tables
            table_id_match = re.search(r'table id="([^"]*)"', chunk.get('markdown', ''))
            table_id = table_id_match.group(1) if table_id_match else f"unknown-{i}"
            
            tables.append({
                'chunk': i,
                'table_id': table_id,
                'content': chunk.get('markdown', '')[:200] + "..."
            })
    
    print(f"\n📊 Commission tables found: {len(tables)}")
    for table in tables:
        print(f"   Chunk {table['chunk']}: Table ID '{table['table_id']}'")
        
        # Show which member precedes this table
        preceding_member = None
        for member in reversed(members):
            if member['chunk'] < table['chunk']:
                preceding_member = member
                break
        
        if preceding_member:
            print(f"      → Associated with: {preceding_member['name']}")
        else:
            print(f"      → No preceding member found!")
        print()

if __name__ == "__main__":
    debug_tables()