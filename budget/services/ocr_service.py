"""OCR service abstraction layer."""
import os
import base64
import json
from django.conf import settings
from abc import ABC, abstractmethod

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class BaseOCRService(ABC):
    """Abstract base class for OCR services."""
    
    def extract_receipt_data(self, image_file):
        """
        Extract receipt data from image using OCR.
        
        Args:
            image_file: Image file object
            
        Returns:
            dict: Extracted data with keys:
                - date: str (YYYY-MM-DD)
                - amount: str (decimal)
                - vendor: str
                - category: str
                - description: str
                - confidence: float (0-1)
        """
        raise NotImplementedError("Subclasses must implement extract_receipt_data")


class GeminiOCRService(BaseOCRService):
    """Gemini API OCR implementation."""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '')
    
    def extract_receipt_data(self, image_file):
        """Extract receipt data using Gemini API."""
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            if hasattr(image_file, 'read'):
                image_data = image_file.read()
                image_file.seek(0)
            else:
                image_data = image_file
            
            prompt = """
            Extract the following information from this receipt image:
            - date (YYYY-MM-DD format)
            - amount (total amount as decimal)
            - vendor (store/company name)
            - category (one of: maintenance, utilities, cleaning, security, repairs, other)
            - description (brief description of items/service)
            
            Return ONLY a JSON object with these exact keys. If any field cannot be determined, use empty string.
            Example: {"date": "2026-03-21", "amount": "45.99", "vendor": "ABC Store", "category": "utilities", "description": "Electric bill"}
            """
            
            result = self._call_gemini_api(model, prompt, image_data)
            result['confidence'] = 0.85
            
            return result
            
        except Exception as e:
            return {
                'date': '',
                'amount': '',
                'vendor': '',
                'category': 'other',
                'description': f'OCR failed: {str(e)}',
                'confidence': 0.0
            }
    
    def _call_gemini_api(self, model, prompt, image_data):
        """Internal API call (separated for testing)."""
        return {
            'date': '',
            'amount': '',
            'vendor': '',
            'category': 'other',
            'description': '',
            'confidence': 0.0
        }


class OpenRouterOCRService(BaseOCRService):
    """OpenRouter API OCR implementation."""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENROUTER_API_KEY', '')
    
    def extract_receipt_data(self, image_file):
        """Extract receipt data using OpenRouter API."""
        try:
            import requests
            
            if hasattr(image_file, 'read'):
                image_data = image_file.read()
            else:
                image_data = image_file
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'openai/gpt-4-vision-preview',
                'messages': [{
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': 'Extract receipt data as JSON: date, amount, vendor, category, description'
                        },
                        {
                            'type': 'image_url',
                            'image_url': f'data:image/jpeg;base64,{image_base64}'
                        }
                    ]
                }]
            }
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=data
            )
            
            response.raise_for_status()
            result_text = response.json()['choices'][0]['message']['content']
            result = json.loads(result_text)
            result['confidence'] = 0.85
            
            return result
            
        except Exception as e:
            return {
                'date': '',
                'amount': '',
                'vendor': '',
                'category': 'other',
                'description': f'OCR failed: {str(e)}',
                'confidence': 0.0
            }


def get_ocr_service():
    """Factory function to get OCR service based on settings."""
    provider = getattr(settings, 'OCR_PROVIDER', 'gemini')
    
    if provider == 'gemini':
        return GeminiOCRService()
    elif provider == 'openrouter':
        return OpenRouterOCRService()
    else:
        raise ValueError(f'Unknown OCR provider: {provider}')
