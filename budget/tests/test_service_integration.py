"""Integration tests for services."""
from django.test import TestCase, override_settings
from budget.services import get_storage_service, get_ocr_service
from budget.services.storage_service import GoogleDriveStorage, CloudinaryStorage
from budget.services.ocr_service import GeminiOCRService, OpenRouterOCRService


class TestServiceFactories(TestCase):
    """Test service factory functions."""
    
    @override_settings(STORAGE_PROVIDER='google_drive')
    def test_get_storage_google_drive(self):
        """Test storage factory returns Google Drive."""
        service = get_storage_service()
        assert isinstance(service, GoogleDriveStorage)
    
    @override_settings(STORAGE_PROVIDER='cloudinary')
    def test_get_storage_cloudinary(self):
        """Test storage factory returns Cloudinary."""
        service = get_storage_service()
        assert isinstance(service, CloudinaryStorage)
    
    @override_settings(OCR_PROVIDER='gemini')
    def test_get_ocr_gemini(self):
        """Test OCR factory returns Gemini."""
        service = get_ocr_service()
        assert isinstance(service, GeminiOCRService)
    
    @override_settings(OCR_PROVIDER='openrouter')
    def test_get_ocr_openrouter(self):
        """Test OCR factory returns OpenRouter."""
        service = get_ocr_service()
        assert isinstance(service, OpenRouterOCRService)
