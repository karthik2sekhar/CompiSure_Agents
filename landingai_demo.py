#!/usr/bin/env python3
"""
LandingAI ADE Integration Example
Demonstrates how to use LandingAI for commission statement extraction
"""

import os
import pandas as pd
from pathlib import Path

# Import the services
from src.landingai_extraction_service import LandingAIExtractionService
from src.commission_processor import CommissionProcessor

def demonstrate_landingai_usage():
    """Demonstrate LandingAI ADE usage for commission extraction"""
    
    print("=== LandingAI ADE Commission Extraction Demo ===\n")
    
    # 1. Initialize the LandingAI service
    print("1. Initializing LandingAI service...")
    landingai_service = LandingAIExtractionService()
    
    if not landingai_service.is_available():
        print("❌ LandingAI service not available")
        print("Please ensure:")
        print("  - VISION_AGENT_API_KEY is set in your .env file")
        print("  - landingai-ade package is installed: pip install landingai-ade")
        return
    
    print("✅ LandingAI service initialized successfully\n")
    
    # 2. Extract data from a sample PDF
    print("2. Extracting commission data from PDF...")
    
    # Find a sample PDF
    docs_dir = Path("docs")
    pdf_files = list(docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in docs directory")
        return
    
    sample_pdf = pdf_files[0]
    print(f"   Processing: {sample_pdf.name}")
    
    # Extract data
    extraction_result = landingai_service.extract_commission_data(
        str(sample_pdf),
        carrier="humana"  # or detect automatically
    )
    
    if "error" in extraction_result:
        print(f"❌ Extraction failed: {extraction_result['error']}")
        return
    
    print("✅ Extraction completed successfully!\n")
    
    # 3. Display extracted information
    print("3. Extracted Information:")
    print(f"   Carrier: {extraction_result.get('carrier', 'Unknown')}")
    print(f"   Statement Date: {extraction_result.get('statement_date', 'Not found')}")
    print(f"   Agent Info: {extraction_result.get('agent_info', {})}")
    print(f"   Total Amount: ${extraction_result.get('total_amount', 0)}")
    print(f"   Commission Entries: {len(extraction_result.get('commission_entries', []))}")
    print()
    
    # 4. Show commission entries
    entries = extraction_result.get('commission_entries', [])
    if entries:
        print("4. Commission Entries (first 5):")
        for i, entry in enumerate(entries[:5], 1):
            print(f"   Entry {i}:")
            print(f"     Policy ID: {entry.get('policy_id', 'N/A')}")
            print(f"     Member: {entry.get('member_name', 'N/A')}")
            print(f"     Amount: ${entry.get('commission_amount', 0)}")
            print(f"     Service Period: {entry.get('service_period', 'N/A')}")
            print()
    
    # 5. Convert to DataFrame
    print("5. Converting to DataFrame...")
    df = landingai_service.to_dataframe(extraction_result)
    
    if not df.empty:
        print(f"✅ DataFrame created with {len(df)} rows")
        print("\nDataFrame columns:", list(df.columns))
        print("\nFirst few rows:")
        print(df.head().to_string())
    else:
        print("❌ DataFrame conversion failed")
    
    print("\n" + "="*60)

def demonstrate_commission_processor_integration():
    """Demonstrate integrated commission processing with LandingAI"""
    
    print("\n=== Commission Processor with LandingAI Integration ===\n")
    
    # 1. Initialize processor
    print("1. Initializing Commission Processor...")
    processor = CommissionProcessor()
    
    print(f"   LandingAI enabled: {processor.use_landingai}")
    print(f"   Fallback methods available: Yes")
    print()
    
    # 2. Process all statements
    print("2. Processing all commission statements...")
    docs_dir = "docs"
    
    if not os.path.exists(docs_dir):
        print("❌ No docs directory found")
        return
    
    results = processor.process_all_statements(docs_dir)
    
    if not results:
        print("❌ No results from processing")
        return
    
    print("✅ Processing completed successfully!\n")
    
    # 3. Display results
    print("3. Processing Results:")
    total_entries = 0
    total_amount = 0.0
    
    for carrier, data in results.items():
        if isinstance(data, dict):
            entries = data.get('commission_entries', [])
            amount = data.get('total_amount', 0)
            extraction_method = data.get('extraction_method', 'unknown')
            
            print(f"   {carrier.upper()}:")
            print(f"     Entries: {len(entries)}")
            print(f"     Total: ${amount}")
            print(f"     Method: {extraction_method}")
            print(f"     Statement Date: {data.get('statement_date', 'N/A')}")
            
            total_entries += len(entries)
            total_amount += amount
        elif isinstance(data, list):
            print(f"   {carrier.upper()}: {len(data)} entries (legacy format)")
            total_entries += len(data)
        
        print()
    
    print(f"Overall Total: {total_entries} entries, ${total_amount}")
    print("\n" + "="*60)

def demonstrate_carrier_specific_extraction():
    """Demonstrate carrier-specific extraction patterns"""
    
    print("\n=== Carrier-Specific Extraction Patterns ===\n")
    
    landingai_service = LandingAIExtractionService()
    
    if not landingai_service.is_available():
        print("❌ LandingAI service not available")
        return
    
    # Show carrier mappings
    print("Supported carrier extraction patterns:")
    
    for carrier, patterns in landingai_service.carrier_mappings.items():
        print(f"\n{carrier.upper()}:")
        print(f"  Statement Date Patterns: {patterns['statement_date_patterns']}")
        print(f"  Policy ID Patterns: {patterns['policy_patterns']}")
        print(f"  Amount Patterns: {patterns['amount_patterns']}")
        print(f"  Table Identifiers: {patterns['table_identifiers']}")
    
    print("\n" + "="*60)

def main():
    """Main demonstration function"""
    
    print("🚀 LandingAI ADE Integration for Commission Reconciliation")
    print("=" * 60)
    
    # Run demonstrations
    demonstrate_landingai_usage()
    demonstrate_commission_processor_integration()
    demonstrate_carrier_specific_extraction()
    
    print("\n🎉 Demo completed!")
    print("\nTo use LandingAI in your system:")
    print("1. Set VISION_AGENT_API_KEY in your .env file")
    print("2. Set USE_LANDING_AI=true in your .env file")
    print("3. Run commission processing as usual - LandingAI will be used automatically")

if __name__ == "__main__":
    main()