# Commission Reconciliation System Configuration

## System Configuration
This file contains configuration options for the Commission Reconciliation System.

### Basic Configuration
```python
{
    'landingai_responses_dir': 'landingai_system_responses',
    'enrollment_file': 'docs/enrollment_info.csv',
    'output_dir': 'commission_reconciliation_reports',
    'email_config': {
        'enabled': False,  # Set to True to enable email reports
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': 'your-email@company.com',
        'sender_password': 'your-app-password',  # Use app password for Gmail
        'recipients': ['manager@company.com', 'accounting@company.com']
    }
}
```

### Adding New Carriers
To add support for new carriers, update the `supported_carriers` configuration:

```python
'supported_carriers': {
    'hne': {
        'name': 'Harvard Pilgrim Health Care',
        'file_pattern': 'HNE_comm_system_response_*.json',
        'table_identifier': 'Incentive ID : Broker Commission'
    },
    'aetna': {
        'name': 'Aetna',
        'file_pattern': 'AETNA_comm_system_response_*.json',
        'table_identifier': 'Commission Summary'  # Update based on actual table identifier
    },
    'cigna': {
        'name': 'Cigna',
        'file_pattern': 'CIGNA_comm_system_response_*.json',
        'table_identifier': 'Agent Commission Report'  # Update based on actual table identifier
    }
}
```

### Email Setup Instructions

#### Gmail Setup:
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: Go to Google Account Settings > Security > App passwords
3. Use the app password (not your regular password) in the configuration
4. Update the sender_email and sender_password in the config

#### Custom SMTP Server:
Update the smtp_server and smtp_port based on your email provider:
- Outlook: `smtp-mail.outlook.com`, port 587
- Yahoo: `smtp.mail.yahoo.com`, port 587
- Custom: Check with your IT department

### File Structure Requirements

The system expects the following structure:
```
project_root/
├── commission_reconciliation_system.py
├── landingai_system_responses/
│   ├── HNE_comm_system_response_YYYYMMDD_HHMMSS.json
│   ├── AETNA_comm_system_response_YYYYMMDD_HHMMSS.json
│   └── ...
├── docs/
│   └── enrollment_info.csv
└── commission_reconciliation_reports/  (created automatically)
    ├── hne_commission_report_YYYYMMDD_HHMMSS.txt
    ├── hne_commission_data_YYYYMMDD_HHMMSS.json
    └── ...
```

### Customizing the System

#### Adding New Extraction Methods:
For each new carrier, add an extraction method in the CommissionReconciliationSystem class:

```python
def extract_aetna_commission_data(self, json_file: str) -> List[Dict[str, Any]]:
    """Extract commission entries from Aetna JSON response."""
    # Implement carrier-specific extraction logic
    pass
```

Then update the `process_carrier_commissions` method to call the new extraction method.

#### Customizing Reports:
Modify the `generate_carrier_report` method to change report format, add new sections, or adjust the layout.

#### Customizing Email Content:
Modify the `create_email_body` method to change email format, subject line, or add additional summary information.

### Matching Logic

The system uses strict matching logic requiring both:
1. **Member ID (Policy ID)** must match exactly
2. **Effective Date** must match exactly (same day)

This ensures accurate reconciliation and prevents false matches.

### Troubleshooting

#### Common Issues:
1. **No files found**: Check file patterns in carrier configuration
2. **Date parsing errors**: Verify date formats in commission statements
3. **Low match rates**: Check enrollment data completeness and date accuracy
4. **Email sending fails**: Verify SMTP settings and authentication

#### Debug Mode:
Add print statements or logging to troubleshoot specific issues:
```python
print(f"Debug: Processing {len(commission_entries)} entries")
print(f"Debug: Found {len(member_matches)} member matches for ID {member_id}")
```