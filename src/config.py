"""
Configuration settings for the Commission Reconciliation System
"""

import os
from typing import Dict, List

class Config:
    """Configuration class for the commission reconciliation system"""
    
    # File processing settings
    SUPPORTED_FILE_FORMATS = ['.pdf', '.xlsx', '.xls', '.csv', '.json']
    
    # Tolerance settings for variance detection
    VARIANCE_TOLERANCE_PERCENTAGE = 0.05  # 5%
    VARIANCE_TOLERANCE_AMOUNT = 10.00  # $10
    
    # Directory settings
    DOCS_DIRECTORY = "docs"
    REPORTS_DIRECTORY = "reports"
    LOGS_DIRECTORY = "logs"
    
    # Carrier-specific settings
    CARRIER_MAPPINGS = {
        'aetna': {
            'name': 'Aetna',
            'file_patterns': ['aetna', 'aet'],
            'expected_columns': ['policy_number', 'commission_amount', 'effective_date']
        },
        'blue_cross': {
            'name': 'Blue Cross Blue Shield',
            'file_patterns': ['blue_cross', 'bluecross', 'bcbs'],
            'expected_columns': ['policy_id', 'commission', 'date']
        },
        'cigna': {
            'name': 'Cigna',
            'file_patterns': ['cigna'],
            'expected_columns': ['policy_number', 'commission_amt', 'commission_date']
        },
        'unitedhealth': {
            'name': 'UnitedHealth Group',
            'file_patterns': ['unitedhealth', 'united_health', 'uhc', 'united'],
            'expected_columns': ['policy_num', 'commission_amount', 'pay_date']
        }
    }
    
    # Commission calculation rules (these would be customized based on actual business rules)
    COMMISSION_RULES = {
        'individual_health': {
            'base_rate': 0.05,  # 5% base commission
            'bonus_threshold': 10000,  # Bonus kicks in after $10k in premiums
            'bonus_rate': 0.01  # Additional 1% bonus
        },
        'group_health': {
            'base_rate': 0.03,  # 3% base commission
            'volume_tiers': {
                50000: 0.005,   # Additional 0.5% for $50k+ volume
                100000: 0.01    # Additional 1% for $100k+ volume
            }
        }
    }
    
    # Report generation settings
    REPORT_SETTINGS = {
        'include_charts': True,
        'chart_formats': ['png'],
        'export_formats': ['excel', 'html', 'pdf', 'json'],
        'chart_dpi': 300,
        'chart_style': 'whitegrid'
    }
    
    # Email notification settings (for future implementation)
    EMAIL_SETTINGS = {
        'enabled': False,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'recipients': [],
        'alert_thresholds': {
            'variance_percentage': 10.0,
            'missing_commission_amount': 1000.0
        }
    }
    
    # Data validation rules
    VALIDATION_RULES = {
        'min_commission_amount': 0.01,
        'max_commission_amount': 50000.00,
        'required_fields': ['amount', 'date'],
        'date_formats': ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S'],
        'outlier_detection': {
            'method': 'iqr',  # interquartile range
            'multiplier': 1.5
        }
    }
    
    @classmethod
    def get_carrier_config(cls, carrier: str) -> Dict:
        """Get configuration for a specific carrier"""
        return cls.CARRIER_MAPPINGS.get(carrier, {})
    
    @classmethod
    def is_supported_format(cls, file_extension: str) -> bool:
        """Check if file format is supported"""
        return file_extension.lower() in cls.SUPPORTED_FILE_FORMATS
    
    @classmethod
    def get_commission_rule(cls, product_type: str) -> Dict:
        """Get commission calculation rules for a product type"""
        return cls.COMMISSION_RULES.get(product_type, {})

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    # Enable email notifications in production
    EMAIL_SETTINGS = {
        **Config.EMAIL_SETTINGS,
        'enabled': True
    }

# Select configuration based on environment
env = os.getenv('COMMISSION_ENV', 'development')
if env == 'production':
    config = ProductionConfig()
else:
    config = DevelopmentConfig()