"""Test suite for storage services."""
import pytest
from django.test import TestCase
from unittest.mock import Mock, patch
from budget.services.storage_service import (
    BaseStorageService,
    GoogleDriveStorage,
    get_storage_service
)


class TestStorageServiceAbstraction(TestCase):
    """Test storage service abstraction."""
    
    def test_base_storage_not_implemented(self):
        """Test BaseStorageService cannot be instantiated directly."""
        with pytest.raises(TypeError):
            service = BaseStorageService()
    
    @patch('budget.services.storage_service.GoogleDriveStorage.upload_file')
    def test_google_drive_upload(self, mock_upload):
        """Test Google Drive upload."""
        mock_upload.return_value = 'https://drive.google.com/file/d/123'
        
        service = GoogleDriveStorage()
        file_mock = Mock()
        url = service.upload_file(file_mock, 'receipt.jpg')
        
        assert url == 'https://drive.google.com/file/d/123'
        mock_upload.assert_called_once_with(file_mock, 'receipt.jpg')
    
    @patch('budget.services.storage_service.settings')
    def test_get_storage_service_google_drive(self, mock_settings):
        """Test factory returns GoogleDriveStorage."""
        mock_settings.STORAGE_PROVIDER = 'google_drive'
        
        service = get_storage_service()
        assert isinstance(service, GoogleDriveStorage)
