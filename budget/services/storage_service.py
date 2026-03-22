"""Storage service abstraction layer."""
import io
from django.conf import settings
from abc import ABC, abstractmethod


class BaseStorageService(ABC):
    """Abstract base class for storage services."""
    
    @abstractmethod
    def upload_file(self, file, filename):
        """
        Upload file to storage.
        
        Args:
            file: File object to upload
            filename: Desired filename
            
        Returns:
            str: URL to uploaded file
        """
        raise NotImplementedError


class GoogleDriveStorage(BaseStorageService):
    """Google Drive storage implementation."""
    
    def __init__(self):
        self.credentials_file = getattr(
            settings,
            'GOOGLE_DRIVE_CREDENTIALS_FILE',
            None
        )
    
    def upload_file(self, file, filename):
        """Upload file to Google Drive."""
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaIoBaseUpload
            from google.oauth2 import service_account
            
            SCOPES = ['https://www.googleapis.com/auth/drive.file']
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=SCOPES
            )
            
            service = build('drive', 'v3', credentials=credentials)
            
            file_metadata = {'name': filename}
            
            if hasattr(file, 'read'):
                file_content = file.read()
            else:
                file_content = file
            
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype='application/octet-stream',
                resumable=True
            )
            
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            return uploaded_file.get('webViewLink')
            
        except Exception as e:
            raise Exception(f'Google Drive upload failed: {str(e)}')
    
    def _upload_to_drive(self, file, filename):
        """Internal method for testing purposes."""
        return self.upload_file(file, filename)


class CloudinaryStorage(BaseStorageService):
    """Cloudinary storage implementation."""
    
    def upload_file(self, file, filename):
        """Upload file to Cloudinary."""
        try:
            import cloudinary
            import cloudinary.uploader
            
            cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL)
            
            result = cloudinary.uploader.upload(
                file,
                public_id=filename,
                resource_type='auto'
            )
            
            return result.get('secure_url')
            
        except Exception as e:
            raise Exception(f'Cloudinary upload failed: {str(e)}')


def get_storage_service():
    """Factory function to get storage service based on settings."""
    provider = getattr(settings, 'STORAGE_PROVIDER', 'google_drive')
    
    if provider == 'google_drive':
        return GoogleDriveStorage()
    elif provider == 'cloudinary':
        return CloudinaryStorage()
    else:
        raise ValueError(f'Unknown storage provider: {provider}')
