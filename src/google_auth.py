"""
Module quản lý xác thực Google Drive API.
Tự động cache token và refresh khi cần.
"""
from pathlib import Path
from typing import Optional

# ============ GOOGLE API IMPORTS ============
GOOGLE_API_AVAILABLE = False
Credentials = None
HttpError = Exception
MediaIoBaseDownload = None
Request = None
InstalledAppFlow = None
build = None

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    pass  # Use fallback values defined above


# ============ CONSTANTS ============
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
TOKEN_FILE = Path('token.json')
CREDENTIALS_FILE = Path('credentials.json')

# MIME Types
GOOGLE_DOC_MIME = 'application/vnd.google-apps.document'
GOOGLE_SHEET_MIME = 'application/vnd.google-apps.spreadsheet'
DOCX_MIME = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


# ============ GOOGLE AUTH CLASS ============
class GoogleAuth:
    """
    Quản lý xác thực Google Drive API.
    
    Features:
        - Cache token tự động
        - Refresh token khi hết hạn
        - OAuth login khi cần thiết
        - Cache Drive service instance
    
    Usage:
        service = GoogleAuth.get_service()
        if service:
            # Use service...
    """
    
    _service = None  # Cache service instance
    
    @classmethod
    def get_credentials(cls) -> Optional[Credentials]:
        """
        Load hoặc tạo mới credentials.
        
        Returns:
            Credentials object hoặc None nếu thất bại
        """
        if not GOOGLE_API_AVAILABLE:
            print("❌ Chưa cài thư viện Google API.")
            return None
        
        creds = None
        
        # Load token cũ
        if TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        
        # Refresh hoặc login mới
        if not creds or not creds.valid:
            creds = cls._refresh_or_login(creds)
        
        return creds
    
    @classmethod
    def _refresh_or_login(cls, creds: Optional[Credentials]) -> Optional[Credentials]:
        """Refresh token cũ hoặc thực hiện OAuth login."""
        # Try refresh
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            cls._save_token(creds)
            return creds
        
        # New login required
        if not CREDENTIALS_FILE.exists():
            print(f"❌ Thiếu file {CREDENTIALS_FILE} (cần tải từ Google Cloud).")
            return None
        
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
        creds = flow.run_local_server(port=0)
        cls._save_token(creds)
        return creds
    
    @classmethod
    def _save_token(cls, creds: Credentials) -> None:
        """Lưu token để dùng lại."""
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    
    @classmethod
    def get_service(cls):
        """
        Lấy Google Drive service (cached).
        
        Returns:
            Drive service object hoặc None
        """
        if cls._service:
            return cls._service
        
        creds = cls.get_credentials()
        if not creds:
            return None
        
        cls._service = build('drive', 'v3', credentials=creds)
        return cls._service
    
    @classmethod
    def reset_service(cls) -> None:
        """Reset cached service (force re-auth)."""
        cls._service = None

