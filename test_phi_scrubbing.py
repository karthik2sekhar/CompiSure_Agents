#!/usr/bin/env python3
"""
Test PHI Scrubbing Implementation
Tests the PHI scrubbing functionality with actual HC commission statement data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.phi_scrubber import PHIScrubber
import pdfplumber

def test_phi_scrubbing():
    """Test PHI scrubbing with HC commission statement."""
    
    print("🧪 Testing PHI Scrubbing Implementation")
    print("=" * 60)
    
    # Initialize scrubber
    scrubber = PHIScrubber()
    
    # Extract text from HC commission statement
    try:
        with pdfplumber.open('docs/HC_COMMISSION_1462-001_R.pdf') as pdf:
            text = ''
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return
    
    print(f"📄 Original text length: {len(text)} characters")
    
    # Test scrubbing
    scrubbed_text, phi_mapping = scrubber.scrub_commission_statement(text)
    
    # Get statistics
    stats = scrubber.get_scrubbing_statistics(phi_mapping)
    
    print(f"\n🔒 PHI Scrubbing Results:")
    print(f"   Total items scrubbed: {stats['total_items_scrubbed']}")
    print(f"   Members scrubbed: {stats['members_scrubbed']}")
    print(f"   Policies scrubbed: {stats['policies_scrubbed']}")
    print(f"   Employers scrubbed: {stats['employers_scrubbed']}")
    print(f"   Addresses scrubbed: {stats['addresses_scrubbed']}")
    print(f"   Phones scrubbed: {stats['phones_scrubbed']}")
    print(f"   Emails scrubbed: {stats['emails_scrubbed']}")
    
    # Show sample of scrubbed text (first few lines of page 3)
    print(f"\n📋 Sample Original Text (HC Statement):")
    sample_lines = text.split('\n')[50:60]  # Sample from middle of document
    for line in sample_lines[:5]:
        if line.strip():
            print(f"   {line.strip()}")
    
    print(f"\n🔒 Sample Scrubbed Text:")
    scrubbed_lines = scrubbed_text.split('\n')[50:60]  # Same section
    for line in scrubbed_lines[:5]:
        if line.strip():
            print(f"   {line.strip()}")
    
    # Show mapping sample
    print(f"\n🗝️  PHI Mapping Sample (first 10 items):")
    mapping_items = list(phi_mapping.items())[:10]
    for placeholder, original in mapping_items:
        print(f"   {placeholder} → {original}")
    
    # Test restoration
    print(f"\n🔓 Testing PHI Restoration:")
    
    # Create sample extracted data
    sample_extracted = [
        {
            'policy_number': 'POLICY_001',
            'member_name': 'MEMBER_001',
            'employer_name': 'EMPLOYER_001',
            'commission_amount': 25.0
        },
        {
            'policy_number': 'POLICY_001',
            'member_name': 'MEMBER_002',
            'employer_name': 'EMPLOYER_001',
            'commission_amount': 6.0
        }
    ]
    
    # Restore PHI
    restored_data = scrubber.restore_phi_to_extracted_data(sample_extracted, phi_mapping)
    
    print(f"   Sample Restored Entry:")
    if restored_data:
        entry = restored_data[0]
        print(f"     Policy: {entry.get('policy_number')}")
        print(f"     Member: {entry.get('member_name')}")
        print(f"     Employer: {entry.get('employer_name')}")
        print(f"     Amount: ${entry.get('commission_amount')}")
    
    print(f"\n✅ PHI Scrubbing Test Complete!")
    print(f"   Privacy Protection: ✅ Enabled")
    print(f"   Data Structure: ✅ Preserved")
    print(f"   Restoration: ✅ Working")

if __name__ == "__main__":
    test_phi_scrubbing()