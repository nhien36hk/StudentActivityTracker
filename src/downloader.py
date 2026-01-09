"""
Module download file Word từ Google Docs.
"""
from pathlib import Path
from typing import Optional
import re
import requests


def extract_doc_id(google_url: str) -> Optional[str]:
    """
    Trích xuất Document ID từ Google Docs URL.
    
    Args:
        google_url: URL Google Docs (dạng /document/d/xxx/edit)
        
    Returns:
        Document ID hoặc None
    """
    # Pattern cho Google Docs URL
    patterns = [
        r'/document/d/([a-zA-Z0-9_-]+)',
        r'/file/d/([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, google_url)
        if match:
            return match.group(1)
    return None


def build_export_url(doc_id: str) -> str:
    """
    Tạo URL export để tải file .docx.
    
    Args:
        doc_id: Google Document ID
        
    Returns:
        URL để download file .docx
    """
    return f"https://docs.google.com/document/d/{doc_id}/export?format=docx"


def download_docx(google_url: str, save_path: Path, timeout: int = 30) -> bool:
    """
    Download file .docx từ Google Docs URL.
    
    Args:
        google_url: URL Google Docs
        save_path: Đường dẫn lưu file
        timeout: Timeout (giây)
        
    Returns:
        True nếu thành công, False nếu thất bại
    """
    doc_id = extract_doc_id(google_url)
    if not doc_id:
        print(f"❌ Không thể extract Doc ID từ: {google_url[:50]}...")
        return False
    
    export_url = build_export_url(doc_id)
    
    try:
        response = requests.get(export_url, timeout=timeout)
        response.raise_for_status()
        
        # Kiểm tra content type
        content_type = response.headers.get('content-type', '')
        if 'application' not in content_type:
            print(f"❌ File không phải document: {content_type}")
            return False
        
        # Lưu file
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(response.content)
        return True
        
    except requests.RequestException as e:
        print(f"❌ Lỗi download: {e}")
        return False


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Làm sạch tên file, loại bỏ ký tự không hợp lệ.
    
    Args:
        filename: Tên file gốc
        max_length: Độ dài tối đa
        
    Returns:
        Tên file đã làm sạch
    """
    # Loại bỏ ký tự không hợp lệ
    invalid_chars = r'[<>:"/\\|?*]'
    clean_name = re.sub(invalid_chars, '_', filename)
    
    # Giới hạn độ dài
    if len(clean_name) > max_length:
        name_part = clean_name[:max_length - 5]
        clean_name = name_part + ".docx"
    
    return clean_name.strip()

