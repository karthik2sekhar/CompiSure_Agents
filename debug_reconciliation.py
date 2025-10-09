#!/usr/bin/env python3
"""
Debug script to test commission reconciliation for HNE and Humana
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from src.commission_processor import CommissionProcessor

# Set up logging to see debug messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')

def test_commission_reconciliation():
    """Test commission processing for HNE and Humana to debug the $0 issue"""
    
    print("Testing commission reconciliation for HNE and Humana...")
    
    try:
        processor = CommissionProcessor()
        
        # Process HNE commission
        print("\n=== PROCESSING HNE ===")
        hne_path = os.path.join('docs', 'HNE comm.pdf')
        if os.path.exists(hne_path):
            results = processor.process_commission_statement(hne_path)
            print(f"HNE Results: {results}")
        else:
            print("HNE commission file not found")
        
        # Process Humana commission
        print("\n=== PROCESSING HUMANA ===")
        humana_path = os.path.join('docs', 'Humana_commission_statement_jul.pdf')
        if os.path.exists(humana_path):
            results = processor.process_commission_statement(humana_path)
            print(f"Humana Results: {results}")
        else:
            print("Humana commission file not found")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_commission_reconciliation()