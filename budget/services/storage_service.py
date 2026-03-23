"""Storage service abstraction layer."""
import io
import logging
from datetime import datetime
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
        self.folder_id_cache = {}
        logger.debug(f"[GOOGLE DRIVE] Config file: {self.credentials_file}")
    
    def _get_or_create_folder(self, service, parent_id, folder_name):
        """Get existing folder ID or create new one."""
        if folder_name in self.folder_id_cache.get(parent_id, {}):
            return self.folder_id_cache[parent_id][folder_name]
        
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = service.files().list(q=query, fields='files(id, name)').execute()
        files = results.get('files', [])
        
        if files:
            folder_id = files[0]['id']
            logger.debug(f"[GOOGLE DRIVE] Found folder: {folder_name} -> {folder_id}")
        else:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                folder_metadata['parents'] = [parent_id]
            
            folder = service.files().create(folder_metadata, fields='id').execute()
            folder_id = folder['id']
            logger.info(f"[GOOGLE DRIVE] Created folder: {folder_name} -> {folder_id}")
        
        if parent_id not in self.folder_id_cache:
            self.folder_id_cache[parent_id] = {}
        self.folder_id_cache[parent_id][folder_name] = folder_id
        
        return folder_id
    
    def _get_year_month_folders(self, service, parent_id=None):
        """Get or create year and month folders."""
        now = datetime.now()
        year_name = str(now.year)
        month_name = now.strftime('%m-%B')
        
        if parent_id:
            root_id = parent_id
        else:
            root_id = self._get_or_create_folder(service, None, 'BudgetControl receipts')
        
        year_id = self._get_or_create_folder(service, root_id, year_name)
        month_id = self._get_or_create_folder(service, year_id, month_name)
        
        return month_id
    
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
            
            parent_folder_id = getattr(settings, 'GOOGLE_DRIVE_PARENT_FOLDER_ID', None)
            folder_id = self._get_year_month_folders(service, parent_folder_id)
            logger.debug(f"[GOOGLE DRIVE] Target folder: {folder_id}")
            
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
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
        self.folder_prefix = getattr(settings, 'CLOUDINARY_FOLDER_PREFIX', 'budget_control')
        logger.debug(f"[CLOUDINARY] Configured with prefix: {self.folder_prefix}")
    
    def _get_folder_path(self):
        """Get year/month folder path."""
        now = datetime.now()
        return f"{self.folder_prefix}/{now.year}/{now.strftime('%m-%B')}"
    
    def upload_file(self, file, filename):
        """Upload file to Cloudinary."""
        logger.debug(f"[CLOUDINARY] Starting upload: {filename}")
        
        try:
            import cloudinary
            import cloudinary.uploader
            
            logger.debug("[CLOUDINARY] Configuring with CLOUDINARY_URL")
            cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL)
            
            folder_path = self._get_folder_path()
            logger.debug(f"[CLOUDINARY] Target folder: {folder_path}")
            
            if hasattr(file, 'read'):
                file_content = file.read()
                file.seek(0)
            else:
                file_content = file
            
            logger.debug(f"[CLOUDINARY] Uploading {len(file_content)} bytes...")
            result = cloudinary.uploader.upload(
                file_content,
                public_id=filename,
                folder=folder_path,
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
