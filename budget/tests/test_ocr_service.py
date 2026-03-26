"""Test suite for OCR services."""
import pytest
from django.test import TestCase
from unittest.mock import Mock, patch
from budget.services.ocr_service import (
    BaseOCRService,
    GeminiOCRService,
    get_ocr_service
)


class TestOCRServiceAbstraction(TestCase):
    """Test OCR service abstraction."""
    
    def test_base_ocr_not_implemented(self):
        """Test BaseOCRService raises NotImplementedError."""
        service = BaseOCRService()
        with pytest.raises(NotImplementedError):
            service.extract_receipt_data(Mock())
    
    @patch('budget.services.ocr_service.genai')
    def test_gemini_ocr_extraction(self, mock_genai):
        """Test Gemini OCR extraction."""
        mock_response = Mock()
        mock_response.text = '{"date": "2026-03-21", "amount": "45.99", "vendor": "Test Store", "category": "Servicios", "description": "Electric bill"}'
        
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client
        
        service = GeminiOCRService()
        file_mock = Mock()
        result = service.extract_receipt_data(file_mock)
        
        assert result['vendor'] == 'Test Store'
        assert result['amount'] == '45.99'
    
    @patch('budget.services.ocr_service.settings')
    def test_get_ocr_service_gemini(self, mock_settings):
        """Test factory returns GeminiOCRService."""
        mock_settings.OCR_PROVIDER = 'gemini'
        
        service = get_ocr_service()
        assert isinstance(service, GeminiOCRService)
