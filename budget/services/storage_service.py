"""Storage service abstraction layer."""
import io
import logging
from django.conf import settings
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


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
        logger.debug(f"[GOOGLE DRIVE] Config file: {self.credentials_file}")
    
    def upload_file(self, file, filename):
        """Upload file to Google Drive."""
        logger.debug(f"[GOOGLE DRIVE] Starting upload: {filename}")
        
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaIoBaseUpload
            from google.oauth2 import service_account
            
            SCOPES = ['https://www.googleapis.com/auth/drive.file']
            
            logger.debug("[GOOGLE DRIVE] Loading credentials...")
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=SCOPES
            )
            
            service = build('drive', 'v3', credentials=credentials)
            logger.debug("[GOOGLE DRIVE] Building Drive service...")
            
            file_metadata = {'name': filename}
            
            if hasattr(file, 'read'):
                file_content = file.read()
            else:
                file_content = file
            
            logger.debug(f"[GOOGLE DRIVE] File content size: {len(file_content)} bytes")
            
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype='application/octet-stream',
                resumable=True
            )
            
            logger.debug("[GOOGLE DRIVE] Uploading file...")
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            url = uploaded_file.get('webViewLink')
            logger.info(f"[GOOGLE DRIVE] Upload successful: {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"[GOOGLE DRIVE] Upload failed: {str(e)}")
            raise Exception(f'Google Drive upload failed: {str(e)}')
    
    def _upload_to_drive(self, file, filename):
        """Internal method for testing purposes."""
        return self.upload_file(file, filename)


class CloudinaryStorage(BaseStorageService):
    """Cloudinary storage implementation."""
    
    def __init__(self):
        logger.debug(f"[CLOUDINARY] Configured")
    
    def upload_file(self, file, filename):
        """Upload file to Cloudinary."""
        logger.debug(f"[CLOUDINARY] Starting upload: {filename}")
        
        try:
            import cloudinary
            import cloudinary.uploader
            
            logger.debug("[CLOUDINARY] Configuring with CLOUDINARY_URL")
            cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL)
            
            if hasattr(file, 'read'):
                file_content = file.read()
                file.seek(0)
            else:
                file_content = file
            
            logger.debug(f"[CLOUDINARY] Uploading {len(file_content)} bytes...")
            result = cloudinary.uploader.upload(
                file_content,
                public_id=filename,
                resource_type='auto'
            )
            
            url = result.get('secure_url')
            logger.info(f"[CLOUDINARY] Upload successful: {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"[CLOUDINARY] Upload failed: {str(e)}")
            raise Exception(f'Cloudinary upload failed: {str(e)}')


def get_storage_service():
    """Factory function to get storage service based on settings."""
    provider = getattr(settings, 'STORAGE_PROVIDER', 'google_drive')
    logger.debug(f"[STORAGE FACTORY] Creating storage service for provider: {provider}")
    
    if provider == 'google_drive':
        return GoogleDriveStorage()
    elif provider == 'cloudinary':
        return CloudinaryStorage()
    else:
        raise ValueError(f'Unknown storage provider: {provider}')
