"""
Module download file từ Google Docs/Sheets.
Hỗ trợ tự động chuyển đổi giữa Public Download và Authenticated API.
"""
import io
import re
from pathlib import Path
from typing import Optional, Tuple

import requests

from src.google_auth import (
    GoogleAuth,
    GOOGLE_API_AVAILABLE,
    GOOGLE_DOC_MIME,
    GOOGLE_SHEET_MIME,
    DOCX_MIME,
    XLSX_MIME,
    HttpError,
    MediaIoBaseDownload,
)


# ============ URL UTILITIES ============
def detect_google_type(url: str) -> str:
    """
    Detect loại file Google từ URL.
    
    Returns:
        'document' | 'spreadsheet' | 'file' | 'unknown'
    """
    if '/document/d/' in url:
        return 'document'
    if '/spreadsheets/d/' in url:
        return 'spreadsheet'
    if '/file/d/' in url:
        return 'file'
    return 'unknown'


def extract_google_id(url: str) -> Optional[str]:
    """Trích xuất File ID từ Google URL."""
    patterns = [
        r'/document/d/([a-zA-Z0-9_-]+)',
        r'/spreadsheets/d/([a-zA-Z0-9_-]+)',
        r'/file/d/([a-zA-Z0-9_-]+)',
    ]
    for pattern in patterns:
        if match := re.search(pattern, url):
            return match.group(1)
    return None


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """Làm sạch tên file, loại bỏ ký tự không hợp lệ."""
    invalid_chars = r'[<>:"/\\|?*]'
    clean_name = re.sub(invalid_chars, '_', filename)
    
    if len(clean_name) > max_length:
        clean_name = clean_name[:max_length - 5] + ".docx"
    
    return clean_name.strip()


# ============ DOWNLOAD: PUBLIC ============
def _build_export_url(file_id: str, file_type: str) -> Tuple[str, str]:
    """Tạo URL export cho Google file."""
    if file_type == 'spreadsheet':
        url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
        return url, 'xlsx'
    
    url = f"https://docs.google.com/document/d/{file_id}/export?format=docx"
    return url, 'docx'


def _download_public(url: str, save_path: Path, timeout: int = 30) -> Tuple[bool, str]:
    """
    Download file công khai bằng requests (nhanh, không cần auth).
    
    Returns:
        (success, file_extension)
    """
    file_id = extract_google_id(url)
    if not file_id:
        return False, ''
    
    file_type = detect_google_type(url)
    export_url, ext = _build_export_url(file_id, file_type)
    
    try:
        response = requests.get(export_url, timeout=timeout)
        response.raise_for_status()
        
        # Check: Nếu trả về HTML => bị redirect login
        content_type = response.headers.get('content-type', '')
        if 'application' not in content_type:
            return False, ''
        
        # Save file
        final_path = save_path.with_suffix(f'.{ext}')
        final_path.parent.mkdir(parents=True, exist_ok=True)
        final_path.write_bytes(response.content)
        return True, ext
        
    except Exception:
        return False, ''


# ============ DOWNLOAD: AUTHENTICATED ============
def _detect_extension(mime_type: str, filename: str) -> str:
    """Xác định extension từ mime type hoặc filename."""
    if '.' in filename:
        return filename.split('.')[-1]
    
    if 'word' in mime_type:
        return 'docx'
    if 'spreadsheet' in mime_type or 'excel' in mime_type:
        return 'xlsx'
    if 'pdf' in mime_type:
        return 'pdf'
    
    return 'bin'


def _create_download_request(service, file_id: str, mime_type: str, filename: str):
    """Tạo request download phù hợp với loại file."""
    # Google Doc gốc -> Export ra DOCX
    if mime_type == GOOGLE_DOC_MIME:
        return service.files().export_media(fileId=file_id, mimeType=DOCX_MIME), 'docx'
    
    # Google Sheet gốc -> Export ra XLSX
    if mime_type == GOOGLE_SHEET_MIME:
        return service.files().export_media(fileId=file_id, mimeType=XLSX_MIME), 'xlsx'
    
    # File binary (Word, PDF...) -> Download trực tiếp
    ext = _detect_extension(mime_type, filename)
    return service.files().get_media(fileId=file_id), ext


def _download_authenticated(url: str, save_path: Path) -> Tuple[bool, str]:
    """
    Download sử dụng Google Drive API.
    Tự động xử lý Google Docs và file binary.
    """
    file_id = extract_google_id(url)
    service = GoogleAuth.get_service()
    
    if not file_id or not service:
        return False, ''
    
    try:
        # Get file metadata
        metadata = service.files().get(fileId=file_id, fields='name, mimeType').execute()
        mime_type = metadata.get('mimeType', '')
        filename = metadata.get('name', 'file')
        print(f"   ℹ️  File Type: {mime_type}")
        
        # Create appropriate request
        request, ext = _create_download_request(service, file_id, mime_type, filename)
        
        # Download
        final_path = save_path.with_suffix(f'.{ext}')
        final_path.parent.mkdir(parents=True, exist_ok=True)
        
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        
        done = False
        while not done:
            _, done = downloader.next_chunk()
        
        final_path.write_bytes(buffer.getbuffer())
        return True, ext
        
    except HttpError as err:
        if err.resp.status == 403:
            print("❌ Lỗi 403: Không có quyền truy cập file này.")
        else:
            print(f"❌ API Error: {err}")
        return False, ''
    except Exception as e:
        print(f"❌ System Error: {e}")
        return False, ''


# ============ MAIN ORCHESTRATOR ============
def download_file(url: str, save_path: Path, timeout: int = 30) -> Tuple[bool, str]:
    """
    Hàm chính download file từ Google.
    
    Strategy:
        1. Thử Public download (nhanh)
        2. Fallback sang Authenticated API nếu cần
    
    Args:
        url: Google Docs/Sheets URL
        save_path: Đường dẫn lưu file (không cần extension)
        timeout: Timeout cho public download
        
    Returns:
        (success, file_extension)
    """
    # Try public first (fast path)
    success, ext = _download_public(url, save_path, timeout)
    if success:
        return True, ext
    
    # Fallback to authenticated
    print(f"⚠️ Link yêu cầu quyền truy cập: {url[:40]}...")
    print("🔄 Đang chuyển sang Google Drive API...")
    
    return _download_authenticated(url, save_path)


# ============ LEGACY SUPPORT ============
def download_docx(url: str, save_path: Path, timeout: int = 30) -> bool:
    """Legacy function - giữ tương thích ngược."""
    success, _ = download_file(url, save_path, timeout)
    return success


# ============ TEST ============
if __name__ == "__main__":
    print("🚀 TEST DOWNLOAD MODULE\n")
    
    test_dir = Path("data/test_downloads")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Test public file
    public_url = "https://docs.google.com/document/d/1wRv7tfpsXJ7VNAZGknCrn7gUhzkyzyggYZh2kVOrSAU/edit"
    save_path = test_dir / "test_public"
    
    print("1️⃣ Test Public Download:")
    success, ext = download_file(public_url, save_path)
    status = "✅ OK" if success else "❌ Failed"
    print(f"   {status} -> {save_path}.{ext}\n")
    
    print("🏁 Done.")
