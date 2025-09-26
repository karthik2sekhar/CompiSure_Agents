"""
Utility functions for the Commission Reconciliation System
"""

import re
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import logging

class DataUtils:
    """Utility functions for data processing and validation"""
    
    @staticmethod
    def clean_currency_string(value: Union[str, float, int]) -> float:
        """
        Clean currency string and convert to float
        
        Args:
            value: Currency value as string, float, or int
            
        Returns:
            Cleaned float value
        """
        if pd.isna(value) or value == '':
            return 0.0
        
        if isinstance(value, (int, float)):
            return float(value)
        
        # Remove currency symbols, commas, and extra spaces
        cleaned = str(value).strip()
        cleaned = re.sub(r'[$,\s]', '', cleaned)
        
        # Handle negative values in parentheses
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def parse_date(date_value: Union[str, datetime], date_formats: List[str] = None) -> Optional[datetime]:
        """
        Parse date from various formats
        
        Args:
            date_value: Date value to parse
            date_formats: List of date formats to try
            
        Returns:
            Parsed datetime object or None
        """
        if pd.isna(date_value) or date_value == '':
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        if date_formats is None:
            date_formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%Y-%m-%d %H:%M:%S',
                '%m/%d/%Y %H:%M:%S',
                '%d/%m/%Y %H:%M:%S',
                '%Y%m%d',
                '%m-%d-%Y',
                '%d-%m-%Y'
            ]
        
        date_str = str(date_value).strip()
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try pandas date parsing as fallback
        try:
            return pd.to_datetime(date_str)
        except:
            return None
    
    @staticmethod
    def identify_column_type(column_name: str, sample_values: List[Any]) -> str:
        """
        Identify the type of data in a column based on name and sample values
        
        Args:
            column_name: Name of the column
            sample_values: Sample values from the column
            
        Returns:
            Identified column type ('amount', 'date', 'policy', 'text', 'id')
        """
        col_lower = column_name.lower().replace('_', '').replace(' ', '')
        
        # Check for amount/currency columns
        amount_keywords = ['amount', 'commission', 'premium', 'fee', 'cost', 'price', 'total', 'sum']
        if any(keyword in col_lower for keyword in amount_keywords):
            return 'amount'
        
        # Check for date columns
        date_keywords = ['date', 'time', 'period', 'effective', 'expiry', 'created', 'modified']
        if any(keyword in col_lower for keyword in date_keywords):
            return 'date'
        
        # Check for policy/ID columns
        id_keywords = ['policy', 'id', 'number', 'num', 'code', 'ref', 'reference']
        if any(keyword in col_lower for keyword in id_keywords):
            return 'policy'
        
        # Analyze sample values
        non_null_values = [v for v in sample_values[:10] if pd.notna(v) and v != '']
        if not non_null_values:
            return 'text'
        
        # Check if values look like currency
        currency_pattern = r'^\$?[\d,]+\.?\d*$'
        currency_count = sum(1 for v in non_null_values if re.match(currency_pattern, str(v).strip()))
        
        if currency_count > len(non_null_values) * 0.7:  # 70% match
            return 'amount'
        
        # Check if values look like dates
        date_patterns = [
            r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'^\d{4}[/-]\d{1,2}[/-]\d{1,2}',
            r'^\d{8}$'  # YYYYMMDD
        ]
        
        date_count = 0
        for value in non_null_values:
            value_str = str(value).strip()
            for pattern in date_patterns:
                if re.match(pattern, value_str):
                    date_count += 1
                    break
        
        if date_count > len(non_null_values) * 0.7:
            return 'date'
        
        return 'text'
    
    @staticmethod
    def detect_outliers(values: List[float], method: str = 'iqr', multiplier: float = 1.5) -> List[bool]:
        """
        Detect outliers in a list of numeric values
        
        Args:
            values: List of numeric values
            method: Method to use ('iqr' or 'zscore')
            multiplier: Multiplier for outlier detection
            
        Returns:
            Boolean list indicating outliers
        """
        if not values:
            return []
        
        values_array = np.array(values)
        
        if method == 'iqr':
            Q1 = np.percentile(values_array, 25)
            Q3 = np.percentile(values_array, 75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR
            
            return [(v < lower_bound or v > upper_bound) for v in values]
        
        elif method == 'zscore':
            mean_val = np.mean(values_array)
            std_val = np.std(values_array)
            
            if std_val == 0:
                return [False] * len(values)
            
            z_scores = np.abs((values_array - mean_val) / std_val)
            return [z > multiplier for z in z_scores]
        
        return [False] * len(values)
    
    @staticmethod
    def standardize_carrier_name(carrier_name: str) -> str:
        """
        Standardize carrier names for consistent processing
        
        Args:
            carrier_name: Original carrier name
            
        Returns:
            Standardized carrier name
        """
        name_lower = carrier_name.lower().strip()
        
        # Mapping of variations to standard names
        name_mappings = {
            'aetna': 'aetna',
            'aet': 'aetna',
            'blue cross': 'blue_cross',
            'bluecross': 'blue_cross',
            'blue cross blue shield': 'blue_cross',
            'bcbs': 'blue_cross',
            'cigna': 'cigna',
            'unitedhealth': 'unitedhealth',
            'united health': 'unitedhealth',
            'united healthcare': 'unitedhealth',
            'uhc': 'unitedhealth',
            'humana': 'humana',
            'anthem': 'anthem'
        }
        
        for pattern, standard in name_mappings.items():
            if pattern in name_lower:
                return standard
        
        # If no match found, return cleaned version
        return re.sub(r'[^\w]', '_', name_lower)

class ValidationUtils:
    """Utility functions for data validation"""
    
    @staticmethod
    def validate_commission_amount(amount: float, min_amount: float = 0.01, max_amount: float = 50000.0) -> bool:
        """
        Validate commission amount is within acceptable range
        
        Args:
            amount: Commission amount to validate
            min_amount: Minimum acceptable amount
            max_amount: Maximum acceptable amount
            
        Returns:
            True if amount is valid
        """
        return min_amount <= amount <= max_amount
    
    @staticmethod
    def validate_date_range(date: datetime, start_date: datetime = None, end_date: datetime = None) -> bool:
        """
        Validate date is within acceptable range
        
        Args:
            date: Date to validate
            start_date: Earliest acceptable date
            end_date: Latest acceptable date
            
        Returns:
            True if date is valid
        """
        if start_date and date < start_date:
            return False
        
        if end_date and date > end_date:
            return False
        
        # Check if date is not too far in the future
        if not end_date:
            future_limit = datetime.now().replace(year=datetime.now().year + 1)
            if date > future_limit:
                return False
        
        return True
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """
        Validate that required fields are present and not empty
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            
        Returns:
            List of missing field names
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in data or pd.isna(data[field]) or data[field] == '':
                missing_fields.append(field)
        
        return missing_fields

class ReportUtils:
    """Utility functions for report generation"""
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format amount as currency string"""
        if pd.isna(amount):
            return "$0.00"
        return f"${amount:,.2f}"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Format value as percentage string"""
        if pd.isna(value):
            return "0.0%"
        return f"{value:.1f}%"
    
    @staticmethod
    def create_summary_table(data: Dict[str, Any]) -> pd.DataFrame:
        """
        Create a summary table from reconciliation data
        
        Args:
            data: Reconciliation results data
            
        Returns:
            Summary DataFrame
        """
        summary_rows = []
        
        for carrier, results in data.items():
            if carrier == 'cross_carrier_analysis':
                continue
            
            summary_rows.append({
                'Carrier': carrier.replace('_', ' ').title(),
                'Total Commissions': ReportUtils.format_currency(results.get('total_commissions', 0)),
                'Expected Commissions': ReportUtils.format_currency(results.get('expected_commissions', 0)),
                'Variance Amount': ReportUtils.format_currency(results.get('variance_amount', 0)),
                'Variance %': ReportUtils.format_percentage(results.get('variance_percentage', 0)),
                'Discrepancies': len(results.get('discrepancies', [])),
                'Status': 'Review Required' if results.get('discrepancies') else 'OK'
            })
        
        return pd.DataFrame(summary_rows)

class LoggingUtils:
    """Utility functions for logging"""
    
    @staticmethod
    def setup_logger(name: str, level: str = 'INFO') -> logging.Logger:
        """
        Set up a logger with consistent formatting
        
        Args:
            name: Logger name
            level: Logging level
            
        Returns:
            Configured logger
        """
        logger = logging.getLogger(name)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, level.upper()))
        
        return logger