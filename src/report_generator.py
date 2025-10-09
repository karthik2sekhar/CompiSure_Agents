"""
Report Generator Module
Generates comprehensive reconciliation reports in multiple formats
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import logging
from jinja2 import Template
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

class ReportGenerator:
    """Generates comprehensive commission reconciliation reports"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        sns.set_style("whitegrid")
        plt.style.use('default')
    
    def generate_reports(self, reconciliation_results: Dict[str, Any], output_dir: str) -> List[str]:
        """
        Generate all reconciliation reports
        
        Args:
            reconciliation_results: Results from reconciliation analysis
            output_dir: Directory to save reports
            
        Returns:
            List of generated report file paths
        """
        report_files = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Generate Excel summary report
            excel_file = self._generate_excel_report(reconciliation_results, output_dir, timestamp)
            if excel_file:
                report_files.append(excel_file)
            
            # Generate detailed HTML report
            html_file = self._generate_html_report(reconciliation_results, output_dir, timestamp)
            if html_file:
                report_files.append(html_file)
            
            # Generate PDF executive summary
            pdf_file = self._generate_pdf_report(reconciliation_results, output_dir, timestamp)
            if pdf_file:
                report_files.append(pdf_file)
            
            # Generate JSON data export
            json_file = self._generate_json_export(reconciliation_results, output_dir, timestamp)
            if json_file:
                report_files.append(json_file)
            
            # Generate visualization charts
            chart_files = self._generate_charts(reconciliation_results, output_dir, timestamp)
            report_files.extend(chart_files)
            
        except Exception as e:
            self.logger.error(f"Error generating reports: {str(e)}")
        
        return report_files
    
    def _generate_excel_report(self, results: Dict[str, Any], output_dir: str, timestamp: str) -> str:
        """Generate comprehensive Excel report with multiple sheets"""
        filename = f"commission_reconciliation_report_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = []
                for carrier, data in results.items():
                    if carrier == 'cross_carrier_analysis' or carrier == 'period_analysis':
                        continue
                    
                    summary_data.append({
                        'Carrier': carrier.replace('_', ' ').title(),
                        'Statement Date': data.get('statement_date', 'Not Available'),
                        'Total Commissions': data.get('total_commissions', 0),
                        'Expected Commissions': data.get('expected_commissions', 0),
                        'Variance Amount': data.get('variance_amount', 0),
                        'Variance %': data.get('variance_percentage', 0),
                        'Discrepancies Count': len(data.get('discrepancies', [])),
                        'Overpayments': len([d for d in data.get('discrepancies', []) if d.get('type') == 'overpayment']),
                        'Underpayments': len([d for d in data.get('discrepancies', []) if d.get('type') == 'underpayment'])
                    })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Individual carrier sheets
                for carrier, data in results.items():
                    if carrier == 'cross_carrier_analysis' or carrier == 'period_analysis':
                        continue
                    
                    sheet_name = carrier.replace('_', ' ').title()[:31]  # Excel sheet name limit
                    
                    # Create carrier detail sheet
                    carrier_data = []
                    
                    # Add summary info
                    carrier_data.append(['Metric', 'Value'])
                    carrier_data.append(['Statement Date', data.get('statement_date', 'Not Available')])
                    carrier_data.append(['Total Commissions', f"${data.get('total_commissions', 0):,.2f}"])
                    carrier_data.append(['Expected Commissions', f"${data.get('expected_commissions', 0):,.2f}"])
                    carrier_data.append(['Variance Amount', f"${data.get('variance_amount', 0):,.2f}"])
                    carrier_data.append(['Variance Percentage', f"{data.get('variance_percentage', 0):.2f}%"])
                    carrier_data.append(['', ''])  # Empty row
                    
                    # Add discrepancies
                    if data.get('discrepancies'):
                        carrier_data.append(['Discrepancies', ''])
                        carrier_data.append(['Type', 'Amount', 'Details'])
                        
                        for disc in data.get('discrepancies', []):
                            carrier_data.append([
                                disc.get('type', ''),
                                f"${disc.get('amount', 0):,.2f}",
                                disc.get('reason', '')
                            ])
                    
                    carrier_df = pd.DataFrame(carrier_data)
                    carrier_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                
                # Cross-carrier analysis sheet
                if 'cross_carrier_analysis' in results:
                    cross_data = results['cross_carrier_analysis']
                    cross_rows = []
                    
                    cross_rows.append(['Cross-Carrier Analysis', ''])
                    cross_rows.append(['Total All Carriers', f"${cross_data.get('total_all_carriers', 0):,.2f}"])
                    cross_rows.append(['', ''])
                    
                    if 'carrier_comparison' in cross_data:
                        cross_rows.append(['Carrier', 'Amount', 'Percentage'])
                        for carrier, comp_data in cross_data['carrier_comparison'].items():
                            cross_rows.append([
                                carrier.replace('_', ' ').title(),
                                f"${comp_data.get('amount', 0):,.2f}",
                                f"{comp_data.get('percentage', 0):.1f}%"
                            ])
                    
                    cross_df = pd.DataFrame(cross_rows)
                    cross_df.to_excel(writer, sheet_name='Cross-Carrier Analysis', index=False, header=False)
            
            self.logger.info(f"Excel report generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating Excel report: {str(e)}")
            return ""
    
    def _generate_html_report(self, results: Dict[str, Any], output_dir: str, timestamp: str) -> str:
        """Generate detailed HTML report"""
        filename = f"commission_reconciliation_report_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Commission Reconciliation Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .header { background-color: #2c5aa0; color: white; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 20px; }
                .summary { background-color: #ffffff; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .carrier-section { margin: 30px 0; border: 1px solid #ddd; border-radius: 8px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .carrier-header { background-color: #e9ecef; padding: 15px; font-weight: bold; font-size: 18px; border-radius: 8px 8px 0 0; }
                .carrier-content { padding: 20px; }
                .variance-section { margin: 20px 0; }
                .variance-header { font-size: 16px; font-weight: bold; margin: 15px 0 10px 0; color: #333; }
                table { width: 100%; border-collapse: collapse; margin: 15px 0; background-color: white; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #f8f9fa; font-weight: bold; color: #495057; }
                .metric { display: inline-block; margin: 10px 30px 10px 0; padding: 8px 0; }
                .metric-label { font-weight: bold; color: #495057; }
                .positive { color: #28a745; font-weight: bold; }
                .negative { color: #dc3545; font-weight: bold; }
                .warning { color: #ffc107; font-weight: bold; }
                .overpayment-row { background-color: #fff3cd; }
                .underpayment-row { background-color: #f8d7da; }
                .variance-summary { background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 10px 0; }
                .alert-success { background-color: #d4edda; border: 1px solid #c3e6cb; padding: 10px; border-radius: 4px; color: #155724; }
                .alert-warning { background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 4px; color: #856404; }
                .alert-danger { background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px; color: #721c24; }
                .no-variances { text-align: center; color: #6c757d; font-style: italic; padding: 20px; }
                .highlight-amount { font-size: 1.1em; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Commission Reconciliation Report</h1>
                <p>Generated on {{ report_date }}</p>
            </div>
            
            <div class="summary">
                <h2>📈 Executive Summary</h2>
                {% if cross_carrier_analysis %}
                <div class="metric">
                    <span class="metric-label">Total Commission (All Carriers):</span> 
                    <span class="highlight-amount">${{ "%.2f"|format(cross_carrier_analysis.total_all_carriers or 0) }}</span>
                </div>
                {% endif %}
                
                <div class="metric">
                    <span class="metric-label">Carriers Processed:</span> {{ carrier_count }}
                </div>
                
                <div class="metric">
                    <span class="metric-label">Total Discrepancies:</span> {{ total_discrepancies }}
                </div>

                <div class="metric">
                    <span class="metric-label">Total Overpayments:</span> 
                    <span class="positive">${{ "%.2f"|format(total_overpayments) }}</span>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Total Underpayments:</span> 
                    <span class="negative">${{ "%.2f"|format(total_underpayments) }}</span>
                </div>
            </div>
            
            {% for carrier, data in carriers.items() %}
            <div class="carrier-section">
                <div class="carrier-header">
                    🏢 {{ carrier.replace('_', ' ').title() }} Commission Analysis
                </div>
                <div class="carrier-content">
                    <div class="variance-summary">
                        <div class="metric">
                            <span class="metric-label">Total Commissions:</span> 
                            <span class="highlight-amount">${{ "%.2f"|format(data.total_commissions or 0) }}</span>
                        </div>
                        
                        <div class="metric">
                            <span class="metric-label">Expected Commissions:</span> 
                            <span class="highlight-amount">${{ "%.2f"|format(data.expected_commissions or 0) }}</span>
                        </div>
                        
                        <div class="metric">
                            <span class="metric-label">Net Variance:</span> 
                            <span class="{% if (data.variance_amount or 0) > 0 %}positive{% elif (data.variance_amount or 0) < 0 %}negative{% endif %}">
                                ${{ "%.2f"|format(data.variance_amount or 0) }} ({{ "%.1f"|format(data.variance_percentage or 0) }}%)
                            </span>
                        </div>
                    </div>
                    
                    {% if data.overpayments %}
                    <div class="variance-section">
                        <div class="variance-header">🔴 Overpayments ({{ data.overpayments|length }} subscribers)</div>
                        <div class="alert-warning">
                            Total Overpaid: <strong>${{ "%.2f"|format(data.overpayments|sum(attribute='amount')) }}</strong>
                        </div>
                        <table>
                            <thead>
                                <tr>
                                    <th>Policy ID</th>
                                    <th>Subscriber Name</th>
                                    <th>Overpayment Amount</th>
                                    <th>Percentage Over</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for overpayment in data.overpayments %}
                                <tr class="overpayment-row">
                                    <td>{{ overpayment.policy_number }}</td>
                                    <td>{{ overpayment.member_name }}</td>
                                    <td class="positive">${{ "%.2f"|format(overpayment.amount) }}</td>
                                    <td class="positive">{{ "%.1f"|format(overpayment.percentage) }}%</td>
                                    <td>{{ overpayment.reason }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% endif %}
                    
                    {% if data.underpayments %}
                    <div class="variance-section">
                        <div class="variance-header">🔵 Underpayments ({{ data.underpayments|length }} subscribers)</div>
                        <div class="alert-danger">
                            Total Underpaid: <strong>${{ "%.2f"|format(data.underpayments|sum(attribute='amount')) }}</strong>
                        </div>
                        <table>
                            <thead>
                                <tr>
                                    <th>Policy ID</th>
                                    <th>Subscriber Name</th>
                                    <th>Underpayment Amount</th>
                                    <th>Percentage Under</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for underpayment in data.underpayments %}
                                <tr class="underpayment-row">
                                    <td>{{ underpayment.policy_number }}</td>
                                    <td>{{ underpayment.member_name }}</td>
                                    <td class="negative">${{ "%.2f"|format(underpayment.amount) }}</td>
                                    <td class="negative">{{ "%.1f"|format(underpayment.percentage) }}%</td>
                                    <td>{{ underpayment.reason }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% endif %}
                    
                    {% if not data.overpayments and not data.underpayments %}
                    <div class="no-variances">
                        <div class="alert-success">
                            ✅ No significant variances found for this carrier. All commissions are within tolerance thresholds.
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if data.subscriber_variances %}
                    <div class="variance-section">
                        <div class="variance-header">📋 Detailed Subscriber Analysis</div>
                        <table>
                            <thead>
                                <tr>
                                    <th>Policy ID</th>
                                    <th>Subscriber Name</th>
                                    <th>Expected Commission</th>
                                    <th>Actual Commission</th>
                                    <th>Variance Amount</th>
                                    <th>Variance %</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for variance in data.subscriber_variances %}
                                <tr>
                                    <td>{{ variance.policy_id }}</td>
                                    <td>{{ variance.subscriber_name }}</td>
                                    <td>${{ "%.2f"|format(variance.expected_commission) }}</td>
                                    <td>${{ "%.2f"|format(variance.actual_commission) }}</td>
                                    <td class="{% if variance.variance_amount > 0 %}positive{% elif variance.variance_amount < 0 %}negative{% endif %}">
                                        ${{ "%.2f"|format(variance.variance_amount) }}
                                    </td>
                                    <td class="{% if variance.variance_amount > 0 %}positive{% elif variance.variance_amount < 0 %}negative{% endif %}">
                                        {{ "%.1f"|format(variance.variance_percentage) }}%
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
            
            <div style="margin-top: 50px; padding: 20px; text-align: center; color: #666; font-size: 12px; background-color: white; border-radius: 8px;">
                <p>🤖 Generated by Automated Commission Reconciliation System</p>
                <p>Report includes PHI-compliant analysis with pattern-based extraction for enhanced accuracy</p>
            </div>
        </body>
        </html>
        """
        
        try:
            # Calculate totals across all carriers
            total_overpayments = 0
            total_underpayments = 0
            total_discrepancies = 0
            
            # Process variance data for each carrier
            processed_carriers = {}
            for carrier, data in results.items():
                if carrier == 'cross_carrier_analysis':
                    continue
                    
                # Initialize processed data structure with existing data
                processed_data = dict(data)
                
                # The overpayments and underpayments are already structured correctly
                # Just need to calculate totals
                if 'overpayments' in data and data['overpayments']:
                    for overpayment in data['overpayments']:
                        total_overpayments += overpayment.get('amount', 0)
                
                if 'underpayments' in data and data['underpayments']:
                    for underpayment in data['underpayments']:
                        total_underpayments += underpayment.get('amount', 0)
                
                # Ensure subscriber_variances exists (use the existing one or create from data)  
                if 'subscriber_variances' not in processed_data:
                    # If old field name exists, use it, otherwise create empty
                    processed_data['subscriber_variances'] = processed_data.get('employer_variances', [])
                
                # Count discrepancies
                total_discrepancies += len(processed_data.get('discrepancies', []))
                total_discrepancies += len(processed_data.get('overpayments', []))
                total_discrepancies += len(processed_data.get('underpayments', []))
                
                processed_carriers[carrier] = processed_data
            
            # Prepare template data
            template_data = {
                'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'carriers': processed_carriers,
                'cross_carrier_analysis': results.get('cross_carrier_analysis', {}),
                'carrier_count': len(processed_carriers),
                'total_discrepancies': total_discrepancies,
                'total_overpayments': total_overpayments,
                'total_underpayments': total_underpayments
            }
            
            template = Template(html_template)
            html_content = template.render(**template_data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {str(e)}")
            return ""
    
    def _generate_pdf_report(self, results: Dict[str, Any], output_dir: str, timestamp: str) -> str:
        """Generate PDF executive summary report with detailed variance analysis"""
        filename = f"commission_reconciliation_summary_{timestamp}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles for better formatting
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.darkblue
            )
            
            # Carrier analysis heading style
            carrier_heading_style = ParagraphStyle(
                'CarrierHeading',
                parent=styles['Heading3'],
                fontSize=16,
                spaceAfter=15,
                spaceBefore=20,
                textColor=colors.darkblue,
                alignment=0  # Left alignment
            )
            
            # Subsection heading style
            subsection_heading_style = ParagraphStyle(
                'SubsectionHeading',
                parent=styles['Heading4'],
                fontSize=12,
                spaceAfter=8,
                spaceBefore=12,
                textColor=colors.darkred,
                alignment=0  # Left alignment
            )
            
            story.append(Paragraph("Commission Reconciliation Report", title_style))
            story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            
            if 'cross_carrier_analysis' in results:
                cross_data = results['cross_carrier_analysis']
                total_discrepancies = sum(len(v.get('overpayments', [])) + len(v.get('underpayments', [])) for k, v in results.items() if k != 'cross_carrier_analysis')
                summary_text = f"""
                Total Commission Processed: ${cross_data.get('total_all_carriers', 0):,.2f}<br/>
                Number of Carriers: {len([k for k in results.keys() if k != 'cross_carrier_analysis'])}<br/>
                Total Discrepancies: {total_discrepancies}
                """
                story.append(Paragraph(summary_text, styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Carrier breakdown table
            story.append(Paragraph("Carrier Summary", styles['Heading2']))
            
            table_data = [['Carrier', 'Statement Date', 'Total Commissions', 'Variance Amount', 'Discrepancies']]
            
            for carrier, data in results.items():
                if carrier == 'cross_carrier_analysis' or carrier == 'period_analysis':
                    continue
                
                discrepancies_count = len(data.get('overpayments', [])) + len(data.get('underpayments', []))
                table_data.append([
                    carrier.replace('_', ' ').title(),
                    data.get('statement_date', 'N/A'),
                    f"${data.get('total_commissions', 0):,.2f}",
                    f"${data.get('variance_amount', 0):,.2f}",
                    str(discrepancies_count)
                ])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 30))
            
            # Detailed Variance Analysis Section
            story.append(Paragraph("Detailed Variance Analysis", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            # Process each carrier for detailed analysis
            for carrier, data in results.items():
                if carrier in ['cross_carrier_analysis', 'period_analysis']:
                    continue
                
                # Skip carriers with no discrepancies to avoid empty sections
                has_overpayments = data.get('overpayments') and len(data['overpayments']) > 0
                has_underpayments = data.get('underpayments') and len(data['underpayments']) > 0
                has_variances = data.get('subscriber_variances') and len(data['subscriber_variances']) > 0
                
                if not (has_overpayments or has_underpayments or has_variances):
                    continue
                
                story.append(Paragraph(f"{carrier.replace('_', ' ').title()} Analysis", carrier_heading_style))
                
                # Overpayments Table
                if data.get('overpayments') and len(data['overpayments']) > 0:
                    story.append(Paragraph("Overpayments", subsection_heading_style))
                    
                    overpay_data = [['Policy ID', 'Subscriber', 'Overpayment Amount', 'Percentage', 'Reason']]
                    
                    # Create a paragraph style for wrapping text in reason column
                    reason_style = ParagraphStyle(
                        'ReasonStyle',
                        parent=styles['Normal'],
                        fontSize=7,
                        leading=8,
                        leftIndent=2,
                        rightIndent=2
                    )
                    
                    for overpay in data['overpayments']:
                        reason_paragraph = Paragraph(str(overpay.get('reason', 'N/A')), reason_style)
                        overpay_data.append([
                            str(overpay.get('policy_number', 'N/A')),
                            str(overpay.get('member_name', 'N/A'))[:20],  # Slightly truncate for space
                            f"${overpay.get('amount', 0):,.2f}",
                            f"{overpay.get('percentage', 0):.1f}%",
                            reason_paragraph  # Use paragraph for word wrapping
                        ])
                    
                    overpay_table = Table(overpay_data, colWidths=[0.8*inch, 1.2*inch, 1*inch, 0.7*inch, 3.8*inch])
                    overpay_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightyellow),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 7),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Top align for wrapped text
                        ('ALIGN', (4, 1), (4, -1), 'LEFT')  # Left align reason column
                    ]))
                    
                    story.append(overpay_table)
                    story.append(Spacer(1, 10))
                
                # Underpayments Table
                if data.get('underpayments') and len(data['underpayments']) > 0:
                    story.append(Paragraph("Underpayments", subsection_heading_style))
                    
                    underpay_data = [['Policy ID', 'Subscriber', 'Underpayment Amount', 'Percentage', 'Reason']]
                    for underpay in data['underpayments']:
                        reason_paragraph = Paragraph(str(underpay.get('reason', 'N/A')), reason_style)
                        underpay_data.append([
                            str(underpay.get('policy_number', 'N/A')),
                            str(underpay.get('member_name', 'N/A'))[:20],  # Slightly truncate for space
                            f"${underpay.get('amount', 0):,.2f}",
                            f"{underpay.get('percentage', 0):.1f}%",
                            reason_paragraph  # Use paragraph for word wrapping
                        ])
                    
                    underpay_table = Table(underpay_data, colWidths=[0.8*inch, 1.2*inch, 1*inch, 0.7*inch, 3.8*inch])
                    underpay_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightcoral),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 7),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Top align for wrapped text
                        ('ALIGN', (4, 1), (4, -1), 'LEFT')  # Left align reason column
                    ]))
                    
                    story.append(underpay_table)
                    story.append(Spacer(1, 10))
                
                # Subscriber Variance Summary (if not already shown in overpayments/underpayments)
                if not data.get('overpayments') and not data.get('underpayments') and data.get('subscriber_variances') and len(data['subscriber_variances']) > 0:
                    story.append(Paragraph("Subscriber Variance Analysis", subsection_heading_style))
                    
                    variance_data = [['Policy ID', 'Subscriber', 'Expected', 'Actual', 'Variance', 'Variance %']]
                    for variance in data['subscriber_variances']:
                        variance_data.append([
                            str(variance.get('policy_id', 'N/A')),
                            str(variance.get('subscriber_name', 'N/A'))[:25],  # Truncate for space
                            f"${variance.get('expected_commission', 0):,.2f}",
                            f"${variance.get('actual_commission', 0):,.2f}",
                            f"${variance.get('variance_amount', 0):,.2f}",
                            f"{variance.get('variance_percentage', 0):.1f}%"
                        ])
                    
                    variance_table = Table(variance_data, colWidths=[1*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
                    variance_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 7),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                    ]))
                    
                    story.append(variance_table)
                    story.append(Spacer(1, 15))
                
                # Legacy discrepancies section (if any exist)
                if data.get('discrepancies'):
                    story.append(Paragraph("Other Discrepancies:", subsection_heading_style))
                    for disc in data.get('discrepancies', []):
                        disc_type = disc.get('type', '').title()
                        actual_amount = disc.get('actual_amount', 0)
                        expected_amount = disc.get('expected_amount', 0)
                        variance_amount = disc.get('variance_amount', 0)
                        variance_pct = disc.get('variance_percentage', 0)
                        
                        disc_text = f"• {disc_type}: ${abs(variance_amount):,.2f} - Commission variance: Expected ${expected_amount:.2f}, Actual ${actual_amount:.2f}, Variance ${variance_amount:.2f} ({variance_pct:.1f}%)"
                        story.append(Paragraph(disc_text, styles['Normal']))
                
                story.append(Spacer(1, 20))
            
            doc.build(story)
            self.logger.info(f"PDF report generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating PDF report: {str(e)}")
            return ""
    
    def _generate_json_export(self, results: Dict[str, Any], output_dir: str, timestamp: str) -> str:
        """Generate JSON export of all reconciliation data"""
        filename = f"commission_reconciliation_data_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        try:
            # Convert numpy types to Python native types for JSON serialization
            def convert_types(obj):
                if hasattr(obj, 'item'):
                    return obj.item()
                elif isinstance(obj, dict):
                    return {k: convert_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_types(v) for v in obj]
                else:
                    return obj
            
            clean_results = convert_types(results)
            
            with open(filepath, 'w') as f:
                json.dump(clean_results, f, indent=2, default=str)
            
            self.logger.info(f"JSON export generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating JSON export: {str(e)}")
            return ""
    
    def _generate_charts(self, results: Dict[str, Any], output_dir: str, timestamp: str) -> List[str]:
        """Generate visualization charts"""
        chart_files = []
        
        try:
            # Commission by carrier pie chart
            if 'cross_carrier_analysis' in results and results['cross_carrier_analysis'].get('carrier_breakdown'):
                carrier_data = results['cross_carrier_analysis']['carrier_breakdown']
                
                plt.figure(figsize=(10, 8))
                carriers = [k.replace('_', ' ').title() for k in carrier_data.keys()]
                amounts = list(carrier_data.values())
                
                plt.pie(amounts, labels=carriers, autopct='%1.1f%%', startangle=90)
                plt.title('Commission Distribution by Carrier', fontsize=16, fontweight='bold')
                
                chart_file = os.path.join(output_dir, f"commission_by_carrier_{timestamp}.png")
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                plt.close()
                
                chart_files.append(chart_file)
                self.logger.info(f"Pie chart generated: {chart_file}")
            
            # Variance analysis bar chart
            carriers = []
            variances = []
            
            for carrier, data in results.items():
                if carrier == 'cross_carrier_analysis':
                    continue
                
                carriers.append(carrier.replace('_', ' ').title())
                variances.append(data.get('variance_amount', 0))
            
            if carriers and variances:
                plt.figure(figsize=(12, 6))
                colors_list = ['green' if v >= 0 else 'red' for v in variances]
                
                plt.bar(carriers, variances, color=colors_list, alpha=0.7)
                plt.title('Commission Variance by Carrier', fontsize=16, fontweight='bold')
                plt.xlabel('Carrier')
                plt.ylabel('Variance Amount ($)')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
                
                # Add value labels on bars
                for i, v in enumerate(variances):
                    plt.text(i, v + (max(variances) * 0.01), f'${v:,.0f}', 
                            ha='center', va='bottom', fontweight='bold')
                
                chart_file = os.path.join(output_dir, f"variance_analysis_{timestamp}.png")
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                plt.close()
                
                chart_files.append(chart_file)
                self.logger.info(f"Bar chart generated: {chart_file}")
        
        except Exception as e:
            self.logger.error(f"Error generating charts: {str(e)}")
        
        return chart_files