"""OCR service abstraction layer."""
import base64
import json
import logging
from django.conf import settings
from abc import ABC, abstractmethod
from PIL import Image
from pyexpat.errors import messages

from budget.models import Category

logger = logging.getLogger(__name__)

try:
    from google import genai
except ImportError:
    genai = None


class BaseOCRService(ABC):
    """Abstract base class for OCR services."""
    
    def extract_receipt_data(self, image_file:Image.Image):
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
        logger.debug(f"[GEMINI OCR] Initialized with API key: {self.api_key[:10]}...")
    
    def extract_receipt_data(self, image_file):
        """Extract receipt data using Gemini API."""
        logger.debug("[GEMINI OCR] Starting extraction...")
        
        try:
            client = genai.Client(api_key=self.api_key)
            logger.debug("[GEMINI OCR] Model configured")
            
            if hasattr(image_file, 'read'):
                image_data = image_file.read()
                image_file.seek(0)
            else:
                image_data = image_file

            categories = Category.objects.filter(category_type='gasto', is_active=True).order_by('name')
            categories_names = [str(n.name) for n in categories]

            prompt = """
            Extraiga la siguiente informacion de esta imagen del recibo:
            - Fecha (formato AAAA-MM-DD)
            - Importe (total en formato decimal)
            - Proveedor (nombre de la tienda/empresa o en su defecto banca donde proviene el comprobante)
            - Categoria (una de las siguientes: """ + ", ".join(categories_names) + """ o 'Otro' si no se puede determinar)
            - Descripcion (breve descripcion de los articulos/servicios)

            Devuelva UNICAMENTE un objeto JSON con estas claves exactas. Si algun campo no se puede determinar, utilice una cadena vacia.

            Ejemplo: {"date": "2026-03-21", "amount": "45.99", "vendor": "Nequi", "category": "Servicios", "description": "Factura de electricidad"}
"""

            logger.debug(f"[GEMINI OCR] Sending request with prompt: {prompt[:200]}...")

            response = client.models.generate_content(
                model="models/gemini-3.1-flash-lite-preview",
                contents=[prompt, image_data])
            
            logger.debug(f"[GEMINI OCR] Raw response: {response.text}")
            
            result = self._parse_response(response.text)
            logger.info(f"[GEMINI OCR] Parsed result: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"[GEMINI OCR] Error: {str(e)}")
            return {
                'date': '',
                'amount': '',
                'vendor': '',
                'category': 'other',
                'description': f'OCR failed: {str(e)}',
                'confidence': 0.0
            }
    
    def _parse_response(self, response_text):
        """Parse JSON response from Gemini."""
        try:
            text = response_text.strip()
            if text.startswith('```json'):
                text = text[7:]
            elif text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            
            text = text.strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"[GEMINI OCR] JSON parse error: {e}, raw: {response_text}")
            return {
                'date': '',
                'amount': '',
                'vendor': '',
                'category': 'other',
                'description': response_text[:200],
                'confidence': 0.0
            }


class OpenRouterOCRService(BaseOCRService):
    """OpenRouter API OCR implementation."""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENROUTER_API_KEY', '')
        logger.debug(f"[OPENROUTER OCR] Initialized with API key: {self.api_key[:15]}...")
    
    def extract_receipt_data(self, image_file:Image.Image):
        """Extract receipt data using OpenRouter API."""
        logger.debug("[OPENROUTER OCR] Starting extraction...")
        
        try:
            import requests
            
            if hasattr(image_file, 'read'):
                image_data = image_file.read()
            else:
                image_data = image_file
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            logger.debug(f"[OPENROUTER OCR] Image encoded, size: {len(image_base64)} chars")
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'google/gemini-2.0-flash-001',
                'messages': [{
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': 'Extract receipt data as JSON with keys: date, amount, vendor, category, description'
                        },
                        {
                            'type': 'image_url',
                            'image_url': {'url': f'data:image/jpeg;base64,{image_base64}'}
                        }
                    ]
                }]
            }
            
            logger.debug("[OPENROUTER OCR] Sending request to API...")
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            
            logger.debug(f"[OPENROUTER OCR] Response status: {response.status_code}")
            response.raise_for_status()
            
            result_text = response.json()['choices'][0]['message']['content']
            logger.debug(f"[OPENROUTER OCR] Raw response: {result_text[:200]}")
            
            result = json.loads(result_text)
            result['confidence'] = 0.85
            logger.info(f"[OPENROUTER OCR] Parsed result: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"[OPENROUTER OCR] Error: {str(e)}")
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
    logger.debug(f"[OCR FACTORY] Creating OCR service for provider: {provider}")
    
    if provider == 'gemini':
        return GeminiOCRService()
    elif provider == 'openrouter':
        return OpenRouterOCRService()
    else:
        raise ValueError(f'Unknown OCR provider: {provider}')
