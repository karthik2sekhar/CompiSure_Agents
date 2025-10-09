#!/usr/bin/env python3
"""
Test the hybrid extraction approach with PHI scrubbing enabled.
"""

import os
os.environ['USE_PHI_SCRUBBING'] = 'true'

from src.commission_processor import CommissionProcessor

def test_hybrid_extraction():
    """Test the hybrid HC extraction approach."""
    processor = CommissionProcessor()
    
    # Process the HC statement
    data = processor._process_pdf('docs/HC_COMMISSION_1462-001_R.pdf', 'hc')
    
    commissions = data.get('commissions', [])
    total_amount = sum(entry.get('amount', 0) for entry in commissions)
    
    print(f"Hybrid Extraction Results:")
    print(f"Entries extracted: {len(commissions)}")
    print(f"Total amount: ${total_amount:.2f}")
    
    if len(commissions) >= 80 and total_amount >= 1000:
        print("✅ SUCCESS: Hybrid approach achieved high accuracy!")
    else:
        print("⚠️ CONCERN: Results may be incomplete")
        
    return commissions

if __name__ == "__main__":
    test_hybrid_extraction()