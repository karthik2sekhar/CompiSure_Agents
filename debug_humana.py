#!/usr/bin/env python3
"""
Debug script to check Humana extraction
"""
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# Add src to path
sys.path.append('.')
from src.llm_extraction_service import LLMExtractionService
import pdfplumber

def debug_humana():
    """Debug Humana extraction process"""
    
    # Extract text from PDF
    pdf_path = "docs/Humana_commission_statement_jul.pdf"
    
    print("=== Extracting PDF text ===")
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    
    print(f"Extracted text length: {len(full_text)} characters")
    print(f"First 500 chars: {full_text[:500]}")
    
    print("\n=== Using LLM to extract commissions ===")
    try:
        llm_service = LLMExtractionService()
        entries = llm_service.extract_commission_entries(full_text, "humana")
        
        print(f"Number of entries extracted: {len(entries)}")
        
        total_amount = 0
        for i, entry in enumerate(entries):
            print(f"\nEntry {i+1}:")
            print(f"  Policy Number: {entry.get('policy_number')}")
            print(f"  Member Name: {entry.get('member_name')}")
            print(f"  Commission Amount: {entry.get('commission_amount')}")
            print(f"  Amount Field: {entry.get('amount')}")
            print(f"  All fields: {entry}")
            
            # Try to get amount from different possible fields
            amount = entry.get('commission_amount') or entry.get('amount') or 0
            total_amount += amount
        
        print(f"\nTotal commission amount: ${total_amount}")
        
    except Exception as e:
        print(f"Error in LLM extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_humana()