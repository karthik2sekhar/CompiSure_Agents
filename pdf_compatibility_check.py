#!/usr/bin/env python3
"""
PDF Format Diagnostic Tool for Textract Compatibility
"""

import os
import PyPDF2
from pathlib import Path

def analyze_pdf_compatibility():
    """Analyze PDF files for Textract compatibility"""
    print("=== PDF TEXTRACT COMPATIBILITY ANALYSIS ===")
    
    docs_dir = "docs"
    pdf_files = [f for f in os.listdir(docs_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in docs/ directory")
        return
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(docs_dir, pdf_file)
        print(f"\n📄 Analyzing: {pdf_file}")
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Basic info
                num_pages = len(pdf_reader.pages)
                print(f"   📋 Pages: {num_pages}")
                
                # Check if encrypted
                if pdf_reader.is_encrypted:
                    print("   🔒 Status: ENCRYPTED (Textract incompatible)")
                    continue
                else:
                    print("   🔓 Status: Not encrypted")
                
                # Check metadata
                metadata = pdf_reader.metadata
                if metadata:
                    print(f"   📊 Creator: {metadata.get('/Creator', 'Unknown')}")
                    print(f"   📊 Producer: {metadata.get('/Producer', 'Unknown')}")
                
                # Try to extract text from first page
                try:
                    first_page = pdf_reader.pages[0]
                    text_sample = first_page.extract_text()[:200]
                    
                    if text_sample.strip():
                        print("   ✅ Text layer: Present (Good for Textract)")
                        print(f"   📝 Sample: {text_sample[:50]}...")
                    else:
                        print("   ❌ Text layer: Missing/Empty (May need OCR)")
                        
                except Exception as e:
                    print(f"   ⚠️  Text extraction error: {str(e)}")
                
                # File size
                file_size = os.path.getsize(pdf_path)
                file_size_mb = file_size / (1024 * 1024)
                print(f"   📏 Size: {file_size_mb:.1f} MB")
                
                if file_size_mb > 10:
                    print("   ⚠️  Large file - may need to be under 10MB for Textract")
                
        except Exception as e:
            print(f"   ❌ Analysis failed: {str(e)}")
    
    print("\n=== TEXTRACT COMPATIBILITY SUMMARY ===")
    print("📌 Common Textract compatibility issues:")
    print("   • Password-protected PDFs")
    print("   • Scanned documents without text layer")
    print("   • Files over 10MB")
    print("   • Unusual PDF encodings")
    print("   • Some PDF versions or compression methods")
    print("\n💡 Solutions:")
    print("   • Use PDFs with embedded text (not just scanned images)")
    print("   • Ensure files are under 10MB")
    print("   • Remove password protection")
    print("   • Re-save PDFs in standard format if possible")

if __name__ == "__main__":
    analyze_pdf_compatibility()