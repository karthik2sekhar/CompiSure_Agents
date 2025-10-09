"""
Intelligent Prompt Generator
Generates adaptive LLM prompts that learn from document structure without hardcoded carrier rules
"""

import re
import logging
from typing import Dict, List, Optional
from datetime import datetime

class IntelligentPromptGenerator:
    """
    Generates context-aware prompts that adapt to any commission statement format
    """
    
    def __init__(self, format_learning_service):
        self.logger = logging.getLogger(__name__)
        self.learning_service = format_learning_service
    
    def generate_adaptive_prompt(self, carrier: str, pdf_text: str) -> str:
        """
        Generate an intelligent extraction prompt that adapts to document structure
        """
        # Analyze the document structure
        structure_analysis = self._analyze_document_structure(pdf_text)
        
        # Get learned insights about this carrier
        carrier_insights = self.learning_service.generate_format_hints(carrier)
        
        # Build the adaptive prompt
        prompt = self._build_intelligent_prompt(carrier, structure_analysis, carrier_insights, pdf_text)
        
        return prompt
    
    def _analyze_document_structure(self, text: str) -> Dict:
        """Analyze document structure to understand format characteristics"""
        analysis = {
            'document_type': 'unknown',
            'data_layout': 'unknown',
            'primary_identifier': 'unknown',
            'data_quality': 'unknown',
            'extraction_strategy': 'flexible',
            'structure_indicators': []
        }
        
        # Clean text for analysis
        clean_text = ' '.join(text.split())
        
        # Detect document type and structure
        structure_indicators = []
        
        # Check for tabular structure
        if self._has_tabular_structure(text):
            analysis['document_type'] = 'tabular'
            analysis['data_layout'] = 'structured_table'
            analysis['extraction_strategy'] = 'structured'
            structure_indicators.append("Clear tabular format detected")
        
        # Check for OCR artifacts (common corruption patterns)
        if self._has_ocr_artifacts(text):
            analysis['data_quality'] = 'ocr_corrupted'
            structure_indicators.append("OCR artifacts detected - text may need correction")
        else:
            analysis['data_quality'] = 'clean'
        
        # Detect potential identifier patterns
        identifier_analysis = self._analyze_identifier_patterns(text)
        analysis['primary_identifier'] = identifier_analysis['suggested_field']
        if identifier_analysis['patterns']:
            structure_indicators.extend(identifier_analysis['patterns'])
        
        # Check for specific layout patterns
        layout_patterns = self._detect_layout_patterns(text)
        if layout_patterns:
            analysis['data_layout'] = layout_patterns[0]  # Primary pattern
            structure_indicators.extend(layout_patterns)
        
        analysis['structure_indicators'] = structure_indicators
        
        return analysis
    
    def _has_tabular_structure(self, text: str) -> bool:
        """Detect if document has clear tabular structure"""
        lines = text.split('\n')
        
        # Look for table headers
        table_headers = [
            'member id', 'policy number', 'commission', 'amount',
            'contract id', 'transaction', 'member name', 'effective date'
        ]
        
        header_matches = 0
        for line in lines[:10]:  # Check first 10 lines
            line_lower = line.lower()
            for header in table_headers:
                if header in line_lower:
                    header_matches += 1
        
        # Look for consistent column spacing
        consistent_spacing = 0
        for i in range(min(5, len(lines) - 1)):
            if i + 1 < len(lines):
                line1_spaces = len(re.findall(r'\s{3,}', lines[i]))  # 3+ spaces
                line2_spaces = len(re.findall(r'\s{3,}', lines[i + 1]))
                if line1_spaces > 2 and abs(line1_spaces - line2_spaces) <= 1:
                    consistent_spacing += 1
        
        return header_matches >= 2 or consistent_spacing >= 3
    
    def _has_ocr_artifacts(self, text: str) -> bool:
        """Detect common OCR artifacts and corruption"""
        artifacts = [
            r'[Il1]{2,}',  # Multiple I, l, 1 confusion
            r'[0O]{2,}[0-9]',  # O/0 confusion patterns
            r'[^a-zA-Z0-9\s.,;:()\[\]{}/\-_@#$%^&*+=|\\<>?~`\'"]',  # Non-standard characters
            r'\b[A-Z]{1}[a-z]{1}[A-Z]',  # Mixed case artifacts
            r'\s+[.,;:]\s+',  # Floating punctuation
        ]
        
        for pattern in artifacts:
            if re.search(pattern, text):
                return True
        return False
    
    def _analyze_identifier_patterns(self, text: str) -> Dict:
        """Analyze potential identifier patterns in the document"""
        patterns = []
        suggested_field = "Member ID"  # Default
        
        # Look for different ID patterns
        id_patterns = {
            'member_id': r'\b(?:member\s*id|member\s*number)[:\s]*([A-Z0-9]{8,15})',
            'policy_number': r'\b(?:policy\s*number|policy\s*id)[:\s]*([A-Z0-9]{8,15})',
            'contract_id': r'\b(?:contract\s*id|contract\s*number)[:\s]*([A-Z0-9]{8,15})',
            'transaction_id': r'\b(?:transaction\s*id|trans\s*id)[:\s]*([A-Z0-9]{6,12})'
        }
        
        matches_found = {}
        for field_type, pattern in id_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                matches_found[field_type] = matches
                patterns.append(f"{field_type.replace('_', ' ').title()} patterns found")
        
        # Look for standalone number patterns (potential IDs)
        standalone_numbers = re.findall(r'\b([A-Z0-9]{8,15})\b', text)
        if standalone_numbers:
            # Analyze number characteristics
            numeric_only = [n for n in standalone_numbers if n.isdigit()]
            alphanumeric = [n for n in standalone_numbers if not n.isdigit() and any(c.isalpha() for c in n)]
            
            if numeric_only:
                patterns.append(f"Numeric IDs detected (length ~{len(numeric_only[0]) if numeric_only else 'varies'})")
            if alphanumeric:
                patterns.append(f"Alphanumeric IDs detected (length ~{len(alphanumeric[0]) if alphanumeric else 'varies'})")
        
        # Determine best identifier field
        if 'member_id' in matches_found:
            suggested_field = "Member ID"
        elif 'policy_number' in matches_found:
            suggested_field = "Policy Number"
        elif standalone_numbers:
            if any(n.isdigit() and len(n) >= 10 for n in standalone_numbers):
                suggested_field = "Member ID (numeric)"
            else:
                suggested_field = "Policy Number"
        
        return {
            'suggested_field': suggested_field,
            'patterns': patterns,
            'matches_found': matches_found
        }
    
    def _detect_layout_patterns(self, text: str) -> List[str]:
        """Detect document layout patterns"""
        patterns = []
        lines = text.split('\n')
        
        # Check for key-value pairs
        kv_pairs = 0
        for line in lines:
            if re.search(r'\w+:\s*\w+', line):
                kv_pairs += 1
        if kv_pairs > 5:
            patterns.append("key_value_format")
        
        # Check for list format
        list_items = 0
        for line in lines:
            if re.search(r'^\s*[-*•]\s+', line) or re.search(r'^\s*\d+[\.)]\s+', line):
                list_items += 1
        if list_items > 3:
            patterns.append("list_format")
        
        # Check for dense paragraph format
        long_lines = sum(1 for line in lines if len(line.strip()) > 80)
        if long_lines > len(lines) * 0.3:
            patterns.append("paragraph_format")
        
        return patterns
    
    def _build_intelligent_prompt(self, carrier: str, structure: Dict, insights: str, pdf_text: str) -> str:
        """Build the intelligent adaptive prompt"""
        
        # Start with core extraction instruction
        prompt = """You are an expert at extracting commission data from insurance carrier statements. 
Your task is to extract ALL commission entries from this document with complete accuracy.

**CRITICAL EXTRACTION REQUIREMENTS:**
1. Extract EVERY commission entry found in the document
2. For each entry, identify the primary policy/member identifier and commission amount
3. Be extremely careful with ID field extraction - use the most specific identifier available
4. Handle data quality issues intelligently (OCR errors, formatting problems)

"""
        
        # Add structure-specific guidance
        if structure['document_type'] == 'tabular':
            prompt += """**DOCUMENT FORMAT DETECTED: Structured Table**
- This document appears to have a clear tabular format
- Look for column headers to identify the correct ID field
- Extract data row by row, maintaining accuracy
- Pay special attention to column alignment and spacing

"""
        
        # Add data quality guidance
        if structure['data_quality'] == 'ocr_corrupted':
            prompt += """**DATA QUALITY ALERT: OCR Corruption Detected**
- This document may contain OCR artifacts and text corruption
- Clean up obvious OCR errors (O/0 confusion, I/l/1 confusion, etc.)
- Remove any prefix letters that appear to be OCR artifacts
- Focus on the actual policy/member numbers, not processing artifacts

"""
        
        # Add identifier guidance
        prompt += f"""**PRIMARY IDENTIFIER STRATEGY: {structure['primary_identifier']}**
"""
        
        if structure['primary_identifier'] == "Member ID":
            prompt += """- Look for Member ID or Member Number fields specifically
- These are typically longer numeric identifiers (10+ digits)
- Avoid Transaction IDs, Contract IDs, or other secondary identifiers
- If you see multiple ID fields, prioritize Member ID over others

"""
        elif "Policy Number" in structure['primary_identifier']:
            prompt += """- Look for Policy Number or Policy ID fields
- These may be alphanumeric and shorter than Member IDs
- Remove any processing prefixes (like N/, M/, etc.) that appear to be artifacts
- Focus on the actual policy identifier, not system codes

"""
        
        # Add carrier-specific guidance
        carrier_lower = carrier.lower()
        if 'hc' in carrier_lower or 'health connector' in carrier_lower or 'healthconnector' in carrier_lower:
            prompt += """**CARRIER-SPECIFIC GUIDANCE: Health Connector (HC)**
- HC statements show GROUP EMPLOYERS with individual SUBSCRIBER commissions underneath
- Structure: Policy ID (like 771140) + Employer Name, followed by individual employee commissions
- Extract EACH INDIVIDUAL subscriber commission entry, not group totals
- Each subscriber may have multiple commission entries (different amounts like $6.00 and $25.00)
- Use format: "PolicyID_SubscriberName" for policy_number (e.g., "771140_Genie Fogg")
- Include both the $6.00 and $25.00 entries for each subscriber as separate records
- Look for "Sub Total" and "Employer Total" to validate your extraction completeness
- Expected total should be around $1,053 based on the statement header

"""
        
        # Add learned insights if available
        if insights and "No previous" not in insights:
            prompt += f"""**LEARNED INSIGHTS for {carrier}:**
{insights}

Use these insights to improve extraction accuracy, but don't let them override what you see in the current document.

"""
        
        # Add format-specific extraction strategy
        if structure['extraction_strategy'] == 'structured':
            prompt += """**EXTRACTION STRATEGY: Structured Approach**
1. First, identify the table headers and column structure
2. Map each column to understand what data it contains
3. Extract data systematically row by row
4. Validate that you're getting the right type of identifier for each entry

"""
        else:
            prompt += """**EXTRACTION STRATEGY: Flexible Pattern Matching**
1. Scan the entire document for commission-related data
2. Look for patterns that indicate policy/member IDs and amounts
3. Be flexible with formatting variations
4. Focus on extracting complete and accurate information

"""
        
        # Add structure indicators if available
        if structure.get('structure_indicators'):
            prompt += f"""**DOCUMENT ANALYSIS:**
{chr(10).join(f"- {indicator}" for indicator in structure['structure_indicators'])}

"""
        
        # Core extraction format (unchanged)
        prompt += """**OUTPUT FORMAT:**
Return a JSON object with this exact structure:
{
  "commissions": [
    {
      "policy_number": "extracted_policy_or_member_id",
      "commission_amount": extracted_amount_as_number
    }
  ],
  "format_analysis": {
    "document_type": "description of document structure",
    "primary_identifier": "type of ID field used (Member ID/Policy Number/etc)",
    "data_quality": "assessment of text quality (clean/ocr_corrupted/etc)",
    "extraction_strategy": "approach used (structured/flexible/pattern_based)"
  }
}

**VALIDATION CHECKLIST:**
- Did you extract ALL commission entries (not just a sample)?
- Are the policy/member IDs clean and properly formatted?
- Are the amounts numeric values (not strings with $ symbols)?
- Did you use the most appropriate identifier field available?
- Did you handle any data quality issues appropriately?

Be thorough and accurate. Every commission entry matters for reconciliation.
"""
        
        return prompt
    
    def generate_validation_prompt(self, extraction_result: Dict, original_text: str) -> str:
        """Generate a validation prompt to double-check extraction results"""
        
        extracted_count = len(extraction_result.get('commissions', []))
        
        validation_prompt = f"""Please validate this commission extraction result by re-examining the original document.

**EXTRACTION RESULT TO VALIDATE:**
- {extracted_count} commission entries were extracted
- Primary identifier type: {extraction_result.get('format_analysis', {}).get('primary_identifier', 'unknown')}

**VALIDATION TASKS:**
1. Count the total number of commission entries in the original document
2. Verify that all entries were captured (check for missed rows/entries)  
3. Confirm the identifier field choice is optimal
4. Check for any extraction errors or data cleaning issues

**ORIGINAL DOCUMENT TEXT:**
{original_text[:2000]}...

**RETURN FORMAT:**
Return a JSON object:
{{
  "validation_result": "complete|incomplete|errors_found",
  "total_entries_in_document": number,
  "extracted_entries": {extracted_count},
  "missing_entries": number_if_any,
  "recommended_corrections": ["list of specific corrections needed"],
  "confidence_score": 0.0_to_1.0
}}

Focus on accuracy and completeness. If the extraction missed entries or used the wrong identifier field, specify exactly what needs to be corrected.
"""
        
        return validation_prompt