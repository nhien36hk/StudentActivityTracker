"""
Module download file từ Google Docs/Sheets.
"""
from pathlib import Path
from typing import Optional, Tuple
import re
import requests


# ============ FILE TYPE DETECTION ============
def detect_google_type(google_url: str) -> str:
    """
    Detect loại file Google từ URL.
    
    Returns:
        'document', 'spreadsheet', 'file', hoặc 'unknown'
    """
    if '/document/d/' in google_url:
        return 'document'
    elif '/spreadsheets/d/' in google_url:
        return 'spreadsheet'
    elif '/file/d/' in google_url:
        return 'file'
    return 'unknown'


# ============ EXTRACT ID ============
def extract_google_id(google_url: str) -> Optional[str]:
    """
    Trích xuất ID từ Google URL (Docs, Sheets, Drive).
    
    Returns:
        Google ID hoặc None
    """
    patterns = [
        r'/document/d/([a-zA-Z0-9_-]+)',
        r'/spreadsheets/d/([a-zA-Z0-9_-]+)',
        r'/file/d/([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, google_url)
        if match:
            return match.group(1)
    return None


# ============ BUILD EXPORT URL ============
def build_export_url(google_id: str, file_type: str) -> str:
    """
    Tạo URL export dựa vào loại file.
    """
    if file_type == 'spreadsheet':
        return f"https://docs.google.com/spreadsheets/d/{google_id}/export?format=xlsx"
    else:
        return f"https://docs.google.com/document/d/{google_id}/export?format=docx"


# ============ DOWNLOAD ============
def download_file(google_url: str, save_path: Path, timeout: int = 30) -> Tuple[bool, str]:
    """
    Download file từ Google URL (tự detect loại).
    
    Returns:
        Tuple (success, file_type) - file_type là 'docx' hoặc 'xlsx'
    """
    file_type = detect_google_type(google_url)
    google_id = extract_google_id(google_url)
    
    if not google_id:
        print(f"❌ Không thể extract ID từ: {google_url[:50]}...")
        return False, ''
    
    export_url = build_export_url(google_id, file_type)
    ext = 'xlsx' if file_type == 'spreadsheet' else 'docx'
    
    try:
        response = requests.get(export_url, timeout=timeout)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '')
        if 'application' not in content_type:
            print(f"❌ File không phải document: {content_type}")
            return False, ''
        
        # Đổi extension nếu cần
        if save_path.suffix != f'.{ext}':
            save_path = save_path.with_suffix(f'.{ext}')
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(response.content)
        return True, ext
        
    except requests.RequestException as e:
        print(f"❌ Lỗi download: {e}")
        return False, ''


# ============ LEGACY SUPPORT ============
def download_docx(google_url: str, save_path: Path, timeout: int = 30) -> bool:
    """Legacy function - giữ tương thích ngược."""
    success, _ = download_file(google_url, save_path, timeout)
    return success


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Làm sạch tên file, loại bỏ ký tự không hợp lệ.
    
    Args:
        filename: Tên file gốc
        max_length: Độ dài tối đa
        
    Returns:
        Tên file đã làm sạch
    """
    invalid_chars = r'[<>:"/\\|?*]'
    clean_name = re.sub(invalid_chars, '_', filename)
    
    if len(clean_name) > max_length:
        name_part = clean_name[:max_length - 5]
        clean_name = name_part + ".docx"
    
    return clean_name.strip()
