"""
Reconciliation Engine Module
Performs variance analysis and identifies discrepancies in commission data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging

class ReconciliationEngine:
    """Engine for performing commission reconciliation and variance analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tolerance_percentage = 0.05  # 5% tolerance for variance detection
        self.tolerance_amount = 10.00  # $10 absolute tolerance
    
    def reconcile_commissions(self, commission_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive reconciliation analysis on commission data
        
        Args:
            commission_data: Dictionary of commission data by carrier
            
        Returns:
            Dictionary containing reconciliation results and analysis
        """
        reconciliation_results = {}
        
        for carrier, data in commission_data.items():
            self.logger.info(f"Reconciling commissions for {carrier}")
            
            carrier_results = {
                'carrier': carrier,
                'total_commissions': 0,
                'expected_commissions': 0,
                'variance_amount': 0,
                'variance_percentage': 0,
                'discrepancies': [],
                'missing_commissions': [],
                'overpayments': [],
                'underpayments': [],
                'summary_stats': {},
                'year_to_date': {}
            }
            
            # Calculate totals and perform analysis
            carrier_results.update(self._analyze_carrier_data(data))
            carrier_results.update(self._detect_discrepancies(data))
            carrier_results.update(self._calculate_variance(data))
            carrier_results.update(self._year_to_date_analysis(data))
            
            reconciliation_results[carrier] = carrier_results
        
        # Perform cross-carrier analysis
        reconciliation_results['cross_carrier_analysis'] = self._cross_carrier_analysis(commission_data)
        
        return reconciliation_results
    
    def _analyze_carrier_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze commission data for a specific carrier"""
        analysis = {
            'total_commissions': 0,
            'commission_count': 0,
            'average_commission': 0,
            'summary_stats': {}
        }
        
        commissions = data.get('commissions', [])
        if not commissions:
            self.logger.warning(f"No commission entries found for carrier: {data.get('carrier', 'Unknown')}")
            return analysis
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(commissions)
        
        # Find commission amount column
        amount_columns = ['amount', 'commission', 'commission_amount', 'total']
        amount_col = None
        
        for col in amount_columns:
            if col in df.columns:
                amount_col = col
                break
        
        if amount_col is None:
            # Try to find any numeric column that might be commission
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                amount_col = numeric_cols[0]
        
        if amount_col:
            # Ensure the column is numeric
            df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')
            df = df.dropna(subset=[amount_col])
            
            analysis['total_commissions'] = float(df[amount_col].sum())
            analysis['commission_count'] = len(df)
            analysis['average_commission'] = float(df[amount_col].mean()) if len(df) > 0 else 0
            
            analysis['summary_stats'] = {
                'min_commission': float(df[amount_col].min()),
                'max_commission': float(df[amount_col].max()),
                'median_commission': float(df[amount_col].median()),
                'std_deviation': float(df[amount_col].std()) if len(df) > 1 else 0
            }
        
        return analysis
    
    def _detect_discrepancies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect various types of discrepancies in commission data"""
        discrepancies = {
            'discrepancies': [],
            'missing_commissions': [],
            'duplicate_entries': [],
            'outliers': []
        }
        
        commissions = data.get('commissions', [])
        if not commissions:
            return discrepancies
        
        df = pd.DataFrame(commissions)
        
        # Find commission amount column
        amount_columns = ['amount', 'commission', 'commission_amount', 'total']
        amount_col = None
        
        for col in amount_columns:
            if col in df.columns:
                amount_col = col
                break
        
        if amount_col is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                amount_col = numeric_cols[0]
        
        if amount_col:
            df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')
            df = df.dropna(subset=[amount_col])
            
            # Detect outliers using IQR method
            Q1 = df[amount_col].quantile(0.25)
            Q3 = df[amount_col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[amount_col] < lower_bound) | (df[amount_col] > upper_bound)]
            
            for _, row in outliers.iterrows():
                discrepancies['outliers'].append({
                    'type': 'outlier',
                    'amount': float(row[amount_col]),
                    'details': dict(row),
                    'reason': f'Amount ${row[amount_col]:,.2f} is outside normal range (${lower_bound:.2f} - ${upper_bound:.2f})'
                })
            
            # Detect potential duplicates
            if 'policy_number' in df.columns:
                duplicates = df[df.duplicated(['policy_number'], keep=False)]
                
                for policy in duplicates['policy_number'].unique():
                    policy_entries = duplicates[duplicates['policy_number'] == policy]
                    discrepancies['duplicate_entries'].append({
                        'type': 'duplicate',
                        'policy_number': policy,
                        'count': len(policy_entries),
                        'total_amount': float(policy_entries[amount_col].sum()),
                        'entries': policy_entries.to_dict('records')
                    })
            
            # Detect variance discrepancies (actual vs expected)
            for commission in commissions:
                actual_amount = commission.get('commission', commission.get('amount', 0))
                expected_amount = commission.get('expected_commission', 0)
                
                if actual_amount is None:
                    actual_amount = 0
                if expected_amount is None:
                    expected_amount = 0
                
                actual_amount = float(actual_amount)
                expected_amount = float(expected_amount)
                
                variance = actual_amount - expected_amount
                variance_pct = (variance / expected_amount * 100) if expected_amount > 0 else 0
                
                # Check if variance exceeds tolerance
                if (abs(variance) > self.tolerance_amount and 
                    abs(variance_pct) > self.tolerance_percentage * 100 and
                    expected_amount > 0):
                    
                    discrepancy_type = 'overpayment' if variance > 0 else 'underpayment'
                    discrepancies['discrepancies'].append({
                        'type': discrepancy_type,
                        'policy_number': commission.get('policy_number', ''),
                        'actual_amount': actual_amount,
                        'expected_amount': expected_amount,
                        'variance_amount': variance,
                        'variance_percentage': variance_pct,
                        'details': commission,
                        'reason': f"Commission variance: Expected ${expected_amount:.2f}, Actual ${actual_amount:.2f}, Variance ${variance:.2f} ({variance_pct:.1f}%)"
                    })
            
            # Detect zero or negative commissions
            zero_negative = df[df[amount_col] <= 0]
            for _, row in zero_negative.iterrows():
                discrepancies['discrepancies'].append({
                    'type': 'zero_or_negative',
                    'amount': float(row[amount_col]),
                    'details': dict(row),
                    'reason': f'Commission amount is ${row[amount_col]:,.2f}'
                })
        
        return discrepancies
    
    def _calculate_variance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate variance against expected commissions with policy-level analysis"""
        variance_analysis = {
            'expected_commissions': 0,
            'actual_commissions': 0,
            'variance_amount': 0,
            'variance_percentage': 0,
            'overpayments': [],
            'underpayments': [],
            'policy_level_variances': []
        }
        
        commissions = data.get('commissions', [])
        if not commissions:
            return variance_analysis
        
        total_actual = 0
        total_expected = 0
        
        # Analyze each policy individually
        for commission in commissions:
            policy_num = commission.get('policy_number', 'Unknown')
            actual_amount = float(commission.get('commission', commission.get('amount', 0)))
            expected_amount = float(commission.get('expected_commission', actual_amount))
            
            total_actual += actual_amount
            total_expected += expected_amount
            
            # Calculate policy-level variance
            variance_amount = actual_amount - expected_amount
            variance_percentage = 0
            if expected_amount > 0:
                variance_percentage = (variance_amount / expected_amount) * 100
            
            # Check if this policy exceeds tolerance thresholds
            if (abs(variance_amount) > self.tolerance_amount or 
                abs(variance_percentage) > self.tolerance_percentage * 100):
                
                policy_variance = {
                    'policy_number': policy_num,
                    'member_name': commission.get('member_name', 'Unknown'),
                    'actual_commission': actual_amount,
                    'expected_commission': expected_amount,
                    'variance_amount': variance_amount,
                    'variance_percentage': variance_percentage
                }
                
                variance_analysis['policy_level_variances'].append(policy_variance)
                
                if variance_amount > 0:
                    variance_analysis['overpayments'].append({
                        'policy_number': policy_num,
                        'member_name': commission.get('member_name', 'Unknown'),
                        'amount': variance_amount,
                        'percentage': variance_percentage,
                        'reason': f'Commission ${actual_amount:.2f} exceeds expected ${expected_amount:.2f}'
                    })
                else:
                    variance_analysis['underpayments'].append({
                        'policy_number': policy_num,
                        'member_name': commission.get('member_name', 'Unknown'),
                        'amount': abs(variance_amount),
                        'percentage': abs(variance_percentage),
                        'reason': f'Commission ${actual_amount:.2f} below expected ${expected_amount:.2f}'
                    })
        
        # Set totals
        variance_analysis['actual_commissions'] = total_actual
        variance_analysis['expected_commissions'] = total_expected
        variance_analysis['variance_amount'] = total_actual - total_expected
        
        if total_expected > 0:
            variance_analysis['variance_percentage'] = ((total_actual - total_expected) / total_expected) * 100
        
        return variance_analysis
    
    def _calculate_expected_commissions(self, data: Dict[str, Any]) -> float:
        """Calculate expected commissions using enrollment data"""
        commissions = data.get('commissions', [])
        if not commissions:
            return 0
        
        # Use expected_commission from enrollment data if available
        total_expected = 0
        for commission in commissions:
            expected_amount = commission.get('expected_commission', 0)
            if expected_amount and expected_amount != 0:
                total_expected += float(expected_amount)
            else:
                # Fallback to actual amount if no expected commission available
                actual_amount = commission.get('commission', commission.get('amount', 0))
                if actual_amount:
                    total_expected += float(actual_amount)
        
        return total_expected
    
    def _year_to_date_analysis(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Perform year-to-date reconciliation analysis"""
        ytd_analysis = {
            'year_to_date': {
                'total_ytd_commissions': 0,
                'monthly_breakdown': {},
                'quarterly_breakdown': {},
                'growth_rate': 0,
                'trend_analysis': {}
            }
        }
        
        commissions = data.get('commissions', [])
        if not commissions:
            return ytd_analysis
        
        df = pd.DataFrame(commissions)
        
        # Try to find date column
        date_columns = ['date', 'commission_date', 'payment_date', 'effective_date']
        date_col = None
        
        for col in date_columns:
            if col in df.columns:
                date_col = col
                break
        
        if date_col:
            try:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                df = df.dropna(subset=[date_col])
                
                # Filter for current year
                current_year = datetime.now().year
                ytd_data = df[df[date_col].dt.year == current_year]
                
                if not ytd_data.empty:
                    # Find amount column
                    amount_columns = ['amount', 'commission', 'commission_amount', 'total']
                    amount_col = None
                    
                    for col in amount_columns:
                        if col in ytd_data.columns:
                            amount_col = col
                            break
                    
                    if amount_col:
                        ytd_data[amount_col] = pd.to_numeric(ytd_data[amount_col], errors='coerce')
                        
                        ytd_analysis['year_to_date']['total_ytd_commissions'] = float(ytd_data[amount_col].sum())
                        
                        # Monthly breakdown
                        monthly = ytd_data.groupby(ytd_data[date_col].dt.month)[amount_col].sum()
                        ytd_analysis['year_to_date']['monthly_breakdown'] = {
                            f"Month_{month}": float(amount) for month, amount in monthly.items()
                        }
                        
                        # Quarterly breakdown
                        quarterly = ytd_data.groupby(ytd_data[date_col].dt.quarter)[amount_col].sum()
                        ytd_analysis['year_to_date']['quarterly_breakdown'] = {
                            f"Q{quarter}": float(amount) for quarter, amount in quarterly.items()
                        }
            
            except Exception as e:
                self.logger.warning(f"Could not perform YTD analysis: {str(e)}")
        
        return ytd_analysis
    
    def _cross_carrier_analysis(self, commission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform analysis across all carriers"""
        cross_analysis = {
            'total_all_carriers': 0,
            'carrier_breakdown': {},
            'top_performing_carrier': '',
            'carrier_comparison': {},
            'overall_statistics': {}
        }
        
        carrier_totals = {}
        
        for carrier, data in commission_data.items():
            summary = data.get('summary', {})
            total = summary.get('total_commission', 0)
            
            if isinstance(total, str):
                try:
                    total = float(total.replace(',', '').replace('$', ''))
                except:
                    total = 0
            
            carrier_totals[carrier] = total
            cross_analysis['total_all_carriers'] += total
        
        cross_analysis['carrier_breakdown'] = carrier_totals
        
        if carrier_totals:
            top_carrier = max(carrier_totals.items(), key=lambda x: x[1])
            cross_analysis['top_performing_carrier'] = {
                'name': top_carrier[0],
                'amount': top_carrier[1]
            }
            
            # Calculate percentages
            total = cross_analysis['total_all_carriers']
            if total > 0:
                for carrier, amount in carrier_totals.items():
                    cross_analysis['carrier_comparison'][carrier] = {
                        'amount': amount,
                        'percentage': (amount / total) * 100
                    }
        
        return cross_analysis