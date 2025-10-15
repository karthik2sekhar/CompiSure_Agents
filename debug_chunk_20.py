import json
import os

def debug_chunk_20():
    """Debug specifically chunk 20 to see why it's not detected"""
    
    # Load Humana JSON response
    response_dir = "landingai_system_responses"
    humana_files = [f for f in os.listdir(response_dir) if f.startswith('Humana_')]
    
    if not humana_files:
        print("❌ No Humana files found")
        return
    
    with open(os.path.join(response_dir, humana_files[0]), 'r') as f:
        response_data = json.load(f)
    
    chunks = response_data['chunks']
    
    # Check chunks 19, 20, 21
    for i in [19, 20, 21]:
        if i < len(chunks):
            chunk = chunks[i]
            print(f"\n📄 Chunk {i}:")
            print(f"   Type: {chunk.get('type', 'Unknown')}")
            
            chunk_markdown = chunk.get('markdown', '')
            print(f"   Has 'Product type': {'Product type' in chunk_markdown}")
            print(f"   Markdown length: {len(chunk_markdown)}")
            
            if 'Product type' in chunk_markdown:
                print(f"   First 300 chars: {chunk_markdown[:300]}")

if __name__ == "__main__":
    debug_chunk_20()