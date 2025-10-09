"""
Format Learning Service
Automatically learns and adapts to different carrier commission statement formats
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

class FormatLearningService:
    """
    Service that learns commission statement formats and improves extraction over time
    """
    
    def __init__(self, learning_file: str = "config/learned_formats.json"):
        self.logger = logging.getLogger(__name__)
        self.learning_file = learning_file
        self.format_cache = self._load_learned_formats()
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.learning_file), exist_ok=True)
    
    def _load_learned_formats(self) -> Dict:
        """Load previously learned formats from disk"""
        try:
            if os.path.exists(self.learning_file):
                with open(self.learning_file, 'r') as f:
                    loaded_data = json.load(f)
                    self.logger.info(f"Loaded learned formats for {len(loaded_data)} carriers")
                    return loaded_data
        except Exception as e:
            self.logger.warning(f"Could not load learned formats: {e}")
        return {}
    
    def _save_learned_formats(self):
        """Save learned formats to disk"""
        try:
            with open(self.learning_file, 'w') as f:
                json.dump(self.format_cache, f, indent=2)
            self.logger.debug("Saved learned formats to disk")
        except Exception as e:
            self.logger.error(f"Could not save learned formats: {e}")
    
    def get_carrier_insights(self, carrier: str) -> Dict:
        """Get learned insights about a specific carrier's format"""
        return self.format_cache.get(carrier.lower(), {})
    
    def learn_from_extraction(self, carrier: str, extraction_result: Dict, success: bool, policy_numbers_extracted: List[str] = None):
        """Learn from extraction results to improve future processing"""
        carrier_key = carrier.lower()
        
        if carrier_key not in self.format_cache:
            self.format_cache[carrier_key] = {
                'extraction_count': 0,
                'successful_extractions': 0,
                'failed_extractions': 0,
                'policy_patterns': [],
                'format_notes': [],
                'success_rate': 0.0,
                'last_successful_extraction': None,
                'last_updated': None
            }
        
        cache_entry = self.format_cache[carrier_key]
        cache_entry['extraction_count'] += 1
        cache_entry['last_updated'] = datetime.now().isoformat()
        
        if success:
            cache_entry['successful_extractions'] += 1
            cache_entry['last_successful_extraction'] = datetime.now().isoformat()
            
            # Learn policy number patterns from successful extractions
            if policy_numbers_extracted:
                for policy_num in policy_numbers_extracted:
                    if policy_num and str(policy_num).strip():
                        # Store unique patterns (avoid duplicates)
                        policy_str = str(policy_num).strip()
                        if policy_str not in cache_entry['policy_patterns']:
                            cache_entry['policy_patterns'].append(policy_str)
                        
                # Keep only recent patterns (last 15)
                cache_entry['policy_patterns'] = cache_entry['policy_patterns'][-15:]
            
            # Learn from extraction metadata if available
            if isinstance(extraction_result, dict) and 'format_analysis' in extraction_result:
                metadata = extraction_result['format_analysis']
                format_note = {
                    'timestamp': datetime.now().isoformat(),
                    'document_type': metadata.get('document_type'),
                    'primary_identifier': metadata.get('primary_identifier'),
                    'data_quality': metadata.get('data_quality'),
                    'extraction_strategy': metadata.get('extraction_strategy')
                }
                cache_entry['format_notes'].append(format_note)
                
                # Keep only recent notes (last 5)
                cache_entry['format_notes'] = cache_entry['format_notes'][-5:]
        else:
            cache_entry['failed_extractions'] += 1
        
        # Update success rate
        cache_entry['success_rate'] = (cache_entry['successful_extractions'] / 
                                     cache_entry['extraction_count']) * 100
        
        self._save_learned_formats()
        
        self.logger.info(f"Learning update for {carrier}: "
                        f"{cache_entry['successful_extractions']}/{cache_entry['extraction_count']} "
                        f"successful ({cache_entry['success_rate']:.1f}%)")
    
    def generate_format_hints(self, carrier: str) -> str:
        """Generate helpful format hints for LLM prompt"""
        insights = self.get_carrier_insights(carrier)
        
        if not insights or insights['successful_extractions'] == 0:
            return "No previous format information available for this carrier."
        
        hints = []
        
        # Success rate information
        success_rate = insights.get('success_rate', 0)
        hints.append(f"Previous success rate: {success_rate:.1f}% ({insights['successful_extractions']}/{insights['extraction_count']})")
        
        # Policy number patterns
        if insights.get('policy_patterns'):
            recent_policies = insights['policy_patterns'][-5:]  # Last 5 examples
            hints.append(f"Recent policy number examples: {', '.join(recent_policies)}")
            
            # Analyze policy patterns
            policy_analysis = self._analyze_policy_patterns(insights['policy_patterns'])
            if policy_analysis:
                hints.append(f"Policy format pattern: {policy_analysis}")
        
        # Latest format insights
        if insights.get('format_notes'):
            latest_note = insights['format_notes'][-1]
            if latest_note.get('document_type'):
                hints.append(f"Document structure: {latest_note['document_type']}")
            if latest_note.get('primary_identifier'):
                hints.append(f"ID field strategy: {latest_note['primary_identifier']}")
            if latest_note.get('data_quality'):
                hints.append(f"Data quality: {latest_note['data_quality']}")
        
        return " | ".join(hints)
    
    def _analyze_policy_patterns(self, policy_numbers: List[str]) -> str:
        """Analyze policy number patterns to provide insights"""
        if not policy_numbers:
            return ""
        
        # Analyze length patterns
        lengths = [len(str(p)) for p in policy_numbers]
        avg_length = sum(lengths) / len(lengths)
        
        # Check for alphanumeric patterns
        has_letters = any(any(c.isalpha() for c in str(p)) for p in policy_numbers)
        all_numeric = all(str(p).isdigit() for p in policy_numbers)
        
        # Check for common prefixes/suffixes
        first_chars = [str(p)[0] for p in policy_numbers if str(p)]
        common_prefix = ""
        if len(set(first_chars)) == 1 and len(first_chars) > 2:
            common_prefix = f"starts with '{first_chars[0]}'"
        
        pattern_parts = []
        pattern_parts.append(f"~{avg_length:.0f} chars")
        
        if all_numeric:
            pattern_parts.append("numeric only")
        elif has_letters:
            pattern_parts.append("alphanumeric")
        
        if common_prefix:
            pattern_parts.append(common_prefix)
        
        return ", ".join(pattern_parts)
    
    def get_learning_statistics(self) -> Dict:
        """Get overall learning statistics"""
        total_carriers = len(self.format_cache)
        total_extractions = sum(carrier.get('extraction_count', 0) for carrier in self.format_cache.values())
        total_successful = sum(carrier.get('successful_extractions', 0) for carrier in self.format_cache.values())
        
        overall_success_rate = (total_successful / total_extractions * 100) if total_extractions > 0 else 0
        
        return {
            'total_carriers_learned': total_carriers,
            'total_extractions_attempted': total_extractions,
            'total_successful_extractions': total_successful,
            'overall_success_rate': overall_success_rate,
            'carriers': {name: {
                'success_rate': data.get('success_rate', 0),
                'extraction_count': data.get('extraction_count', 0),
                'last_updated': data.get('last_updated')
            } for name, data in self.format_cache.items()}
        }
    
    def reset_carrier_learning(self, carrier: str):
        """Reset learning data for a specific carrier"""
        carrier_key = carrier.lower()
        if carrier_key in self.format_cache:
            del self.format_cache[carrier_key]
            self._save_learned_formats()
            self.logger.info(f"Reset learning data for carrier: {carrier}")
        else:
            self.logger.warning(f"No learning data found for carrier: {carrier}")
    
    def export_learning_data(self) -> Dict:
        """Export all learning data for backup or analysis"""
        return {
            'export_timestamp': datetime.now().isoformat(),
            'learning_statistics': self.get_learning_statistics(),
            'format_cache': self.format_cache
        }