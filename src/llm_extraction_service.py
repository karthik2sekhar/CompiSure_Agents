"""
LLM-based PDF extraction service using OpenAI API.
This service extracts commission data from unstructured PDF text using GPT models.
"""

import json
import logging
import os
import re
from typing import List, Dict, Any, Optional
from openai import OpenAI


class LLMExtractionService:
    """Service for extracting commission data from PDF text using LLM."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = self._initialize_client()
        self.model = "gpt-3.5-turbo"  # Cost-efficient model
        
    def _initialize_client(self) -> Optional[OpenAI]:
        """Initialize OpenAI client with API key from environment variable."""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                self.logger.error("OPENAI_API_KEY environment variable not found")
                return None
            
            client = OpenAI(api_key=api_key)
            self.logger.info("OpenAI client initialized successfully")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            return None
    
    def extract_commission_entries(self, pdf_text: str, carrier: str = None) -> List[Dict[str, Any]]:
        """
        Extract commission entries from PDF text using LLM.
        
        Args:
            pdf_text: Raw text extracted from PDF
            carrier: Optional carrier name for context
            
        Returns:
            List of commission entries with extracted fields
        """
        if not self.client:
            self.logger.error("OpenAI client not initialized")
            return []
        
        if not pdf_text.strip():
            self.logger.warning("Empty PDF text provided")
            return []
        
        try:
            prompt = self._create_extraction_prompt(pdf_text, carrier)
            response = self._call_openai_api(prompt)
            entries = self._parse_llm_response(response)
            
            self.logger.info(f"Successfully extracted {len(entries)} commission entries using LLM")
            return entries
            
        except Exception as e:
            self.logger.error(f"Error during LLM extraction: {e}")
            return []
    
    def _create_extraction_prompt(self, pdf_text: str, carrier: str = None) -> str:
        """Create a structured prompt for commission data extraction."""
        
        carrier_context = f" from {carrier}" if carrier else ""
        
        prompt = f"""
You are an expert at extracting commission data from insurance carrier statements{carrier_context}.

Extract ALL commission entries from the following statement text. For each entry, extract these fields:
- policy_number: The policy or certificate number
- amount: The commission amount (as a number, no currency symbols)
- date: The commission date (in YYYY-MM-DD format)
- member_name: The insured member's name (if available)
- product_name: The insurance product type (if available)
- premium: The premium amount (if available)

Return the result as a valid JSON array. If a field is not available, use null.

Example format:
[
  {{
    "policy_number": "AET001234",
    "amount": 1250.00,
    "date": "2024-01-15",
    "member_name": "John Doe",
    "product_name": "Individual Health",
    "premium": 5000.00
  }}
]

Statement text:
{pdf_text}

Extract only the commission entries, return valid JSON:
"""
        return prompt
    
    def _call_openai_api(self, prompt: str) -> str:
        """Make API call to OpenAI and return response."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise data extraction assistant. Always return valid JSON arrays for commission data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0,  # Deterministic responses
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse and validate the LLM JSON response."""
        try:
            # Clean up response if it contains extra text
            response = response.strip()
            
            # Try to find JSON array in the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            else:
                # If no array found, try to parse the whole response as JSON
                json_str = response
            
            # Parse JSON
            parsed_data = json.loads(json_str)
            
            # Ensure we have a list
            if isinstance(parsed_data, dict) and 'entries' in parsed_data:
                parsed_data = parsed_data['entries']
            elif isinstance(parsed_data, dict) and 'commissions' in parsed_data:
                parsed_data = parsed_data['commissions']
            elif not isinstance(parsed_data, list):
                self.logger.warning(f"Unexpected response format: {type(parsed_data)}")
                return []
            
            # Validate and clean entries
            validated_entries = []
            for entry in parsed_data:
                if self._validate_entry(entry):
                    cleaned_entry = self._clean_entry(entry)
                    validated_entries.append(cleaned_entry)
            
            return validated_entries
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM JSON response: {e}")
            self.logger.error(f"Response was: {response}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing LLM response: {e}")
            return []
    
    def _validate_entry(self, entry: Dict[str, Any]) -> bool:
        """Validate that an entry has required fields."""
        required_fields = ['policy_number', 'amount', 'date']
        
        for field in required_fields:
            if field not in entry or entry[field] is None:
                self.logger.warning(f"Entry missing required field '{field}': {entry}")
                return False
        
        # Validate amount is numeric
        try:
            float(entry['amount'])
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid amount in entry: {entry}")
            return False
        
        return True
    
    def _clean_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize an entry."""
        cleaned = {}
        
        # Required fields
        cleaned['policy_number'] = str(entry['policy_number']).strip()
        cleaned['amount'] = float(entry['amount'])
        cleaned['date'] = str(entry['date']).strip()
        
        # Optional fields
        for field in ['member_name', 'product_name', 'premium']:
            if field in entry and entry[field] is not None:
                if field == 'premium':
                    try:
                        cleaned[field] = float(entry[field])
                    except (ValueError, TypeError):
                        cleaned[field] = None
                else:
                    cleaned[field] = str(entry[field]).strip()
            else:
                cleaned[field] = None
        
        return cleaned
    
    def get_extraction_cost_estimate(self, text_length: int) -> Dict[str, float]:
        """Estimate the cost of extraction based on text length."""
        # GPT-3.5-turbo pricing (approximate)
        input_tokens = text_length // 4  # Rough estimate: 4 chars per token
        output_tokens = 500  # Estimated output tokens
        
        input_cost = (input_tokens / 1000) * 0.0015  # $0.0015 per 1K input tokens
        output_cost = (output_tokens / 1000) * 0.002  # $0.002 per 1K output tokens
        total_cost = input_cost + output_cost
        
        return {
            'estimated_input_tokens': input_tokens,
            'estimated_output_tokens': output_tokens,
            'estimated_cost_usd': total_cost
        }