#!/usr/bin/env python3
"""
PDF Generation Test Script
Tests the PDF generation in isolation to debug issues
"""

import sys
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def test_pdf_generation():
    """Test PDF generation with sample data"""
    
    # Load the actual data
    try:
        with open("reports/commission_reconciliation_data_20251006_144439.json", "r") as f:
            results = json.load(f)
    except Exception as e:
        print(f"❌ Could not load data: {e}")
        return False
    
    # Create test PDF
    filepath = "test_detailed_pdf.pdf"
    
    try:
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue
        )
        
        story.append(Paragraph("Test PDF Generation", title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Process HC data
        hc_data = results.get("hc", {})
        if hc_data:
            story.append(Paragraph("HC Analysis", styles['Heading2']))
            
            # Overpayments Table
            overpayments = hc_data.get('overpayments', [])
            if overpayments:
                print(f"📊 Processing {len(overpayments)} overpayments")
                story.append(Paragraph("Overpayments", styles['Heading3']))
                
                overpay_data = [['Policy ID', 'Employer', 'Amount', 'Percentage', 'Reason']]
                for overpay in overpayments:
                    overpay_data.append([
                        str(overpay.get('policy_number', 'N/A')),
                        str(overpay.get('member_name', 'N/A'))[:25],
                        f"${overpay.get('amount', 0):,.2f}",
                        f"{overpay.get('percentage', 0):.1f}%",
                        str(overpay.get('reason', 'N/A'))[:40]
                    ])
                
                overpay_table = Table(overpay_data, colWidths=[1*inch, 1.5*inch, 1*inch, 0.8*inch, 2.2*inch])
                overpay_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightyellow),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (4, 1), (4, -1), 'LEFT')
                ]))
                
                story.append(overpay_table)
                story.append(Spacer(1, 10))
            
            # Underpayments Table
            underpayments = hc_data.get('underpayments', [])
            if underpayments:
                print(f"📊 Processing {len(underpayments)} underpayments")
                story.append(Paragraph("Underpayments", styles['Heading3']))
                
                underpay_data = [['Policy ID', 'Employer', 'Amount', 'Percentage', 'Reason']]
                for underpay in underpayments:
                    underpay_data.append([
                        str(underpay.get('policy_number', 'N/A')),
                        str(underpay.get('member_name', 'N/A'))[:25],
                        f"${underpay.get('amount', 0):,.2f}",
                        f"{underpay.get('percentage', 0):.1f}%",
                        str(underpay.get('reason', 'N/A'))[:40]
                    ])
                
                underpay_table = Table(underpay_data, colWidths=[1*inch, 1.5*inch, 1*inch, 0.8*inch, 2.2*inch])
                underpay_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightcoral),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (4, 1), (4, -1), 'LEFT')
                ]))
                
                story.append(underpay_table)
                story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        
        # Check file size
        file_size = os.path.getsize(filepath)
        print(f"✅ Test PDF generated: {filepath}")
        print(f"📄 Test PDF size: {file_size:,} bytes")
        
        if file_size > 10000:
            print("✅ Test PDF has detailed content")
            return True
        else:
            print("⚠️  Test PDF still small")
            return False
            
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    sys.exit(0 if success else 1)