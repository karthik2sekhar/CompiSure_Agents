"""
Simple test to check LandingAI configuration and run extraction
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Environment check:")
print(f"VISION_AGENT_API_KEY: {os.environ.get('VISION_AGENT_API_KEY', 'NOT_SET')}")
print(f"USE_LANDING_AI: {os.environ.get('USE_LANDING_AI', 'NOT_SET')}")

# Try to initialize LandingAI
try:
    from landingai_ade import LandingAIADE
    print("✅ landingai_ade imported successfully")
    
    api_key = os.environ.get("VISION_AGENT_API_KEY")
    if api_key and api_key != 'your_landingai_api_key_here':
        try:
            client = LandingAIADE(apikey=api_key)
            print("✅ LandingAI client initialized successfully")
            
            # Try parsing a document
            pdf_path = "docs/HC_COMMISSION_1462-001_R.pdf"
            if os.path.exists(pdf_path):
                print(f"📄 Processing: {pdf_path}")
                
                from pathlib import Path
                result = client.parse(
                    document=Path(pdf_path),
                    model="dpt-2-latest"
                )
                
                print("✅ Document parsed successfully")
                
                # Convert to dict and save
                if hasattr(result, 'dict'):
                    data = result.dict()
                elif hasattr(result, 'model_dump'):
                    data = result.model_dump()
                else:
                    data = result
                
                import json
                with open('hc_extraction_debug.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                
                print(f"📁 Raw extraction saved to: hc_extraction_debug.json")
                print(f"📊 Markdown length: {len(data.get('markdown', ''))}")
                print(f"📋 Chunks: {len(data.get('chunks', []))}")
                
                # Show some basic stats
                markdown = data.get('markdown', '')
                print(f"\n📝 Sample markdown (first 200 chars):")
                print("-" * 40)
                print(markdown[:200])
                print("-" * 40)
                
            else:
                print(f"❌ File not found: {pdf_path}")
                
        except Exception as e:
            print(f"❌ Failed to initialize LandingAI client: {str(e)}")
    else:
        print("❌ API key not configured properly")
        
except ImportError as e:
    print(f"❌ landingai_ade import failed: {str(e)}")