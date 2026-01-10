"""
Module extract hyperlinks từ file Excel.
Hỗ trợ cả external links (Google URL) và internal links (sheet trong cùng file).
"""
from pathlib import Path
from typing import List, Tuple, Dict, Any
from openpyxl import load_workbook
import re


def find_link_column(worksheet, header_row: int = 2) -> int | None:
    """Tìm cột chứa link trong worksheet."""
    for col in range(1, worksheet.max_column + 1):
        cell_value = worksheet.cell(row=header_row, column=col).value
        if cell_value and 'link' in str(cell_value).lower():
            return col
    return None


def parse_sheet_location(location: str) -> str | None:
    """
    Parse tên sheet từ internal link location.
    VD: "'TÊN SHEET'!A1" → "TÊN SHEET"
    """
    if not location:
        return None
    match = re.match(r"'(.+?)'!", location)
    if match:
        return match.group(1)
    return None


def extract_links(excel_path: Path, limit: int | None = None) -> List[Dict[str, Any]]:
    """
    Extract danh sách links từ file Excel.
    Tự động detect loại link: external (URL) hoặc internal (sheet).
    
    Args:
        excel_path: Đường dẫn file Excel
        limit: Số lượng link tối đa (None = tất cả)
        
    Returns:
        List các dict với keys:
        - display_text: Tên hiển thị
        - link_type: 'external' hoặc 'internal'
        - url: URL (nếu external)
        - sheet_name: Tên sheet (nếu internal)
    """
    wb = load_workbook(excel_path)
    ws = wb.active
    
    link_col = find_link_column(ws)
    if not link_col:
        raise ValueError("Không tìm thấy cột Link trong file Excel")
    
    links: List[Dict[str, Any]] = []
    header_row = 2
    
    for row in range(header_row + 1, ws.max_row + 1):
        if limit and len(links) >= limit:
            break
            
        cell = ws.cell(row=row, column=link_col)
        if not cell.hyperlink:
            continue
        
        display_text = str(cell.value) if cell.value else ""
        
        # Check external link (có target URL)
        if cell.hyperlink.target:
            links.append({
                'display_text': display_text,
                'link_type': 'external',
                'url': cell.hyperlink.target,
                'sheet_name': None,
            })
        # Check internal link (có location đến sheet khác)
        elif cell.hyperlink.location:
            sheet_name = parse_sheet_location(cell.hyperlink.location)
            if sheet_name and sheet_name in wb.sheetnames:
                # Ưu tiên dùng URL trong cell value nếu có, không thì dùng location
                url = display_text if display_text.startswith('http') else cell.hyperlink.location
                links.append({
                    'display_text': display_text,
                    'link_type': 'internal',
                    'url': url,
                    'sheet_name': sheet_name,
                })
    
    wb.close()
    return links


# Legacy function cho tương thích ngược
def extract_hyperlinks(excel_path: Path, limit: int | None = None) -> List[Tuple[str, str]]:
    """Legacy: Chỉ trả về external links."""
    links = extract_links(excel_path, limit)
    return [(l['display_text'], l['url']) for l in links if l['link_type'] == 'external']

