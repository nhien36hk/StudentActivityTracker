"""
Module extract hyperlinks từ file Excel.
"""
from pathlib import Path
from typing import List, Tuple
from openpyxl import load_workbook


def find_link_column(worksheet, header_row: int = 2) -> int | None:
    """
    Tìm cột chứa link trong worksheet.
    
    Args:
        worksheet: Worksheet của openpyxl
        header_row: Dòng chứa header
        
    Returns:
        Số cột chứa link hoặc None nếu không tìm thấy
    """
    for col in range(1, worksheet.max_column + 1):
        cell_value = worksheet.cell(row=header_row, column=col).value
        if cell_value and 'link' in str(cell_value).lower():
            return col
    return None


def extract_hyperlinks(excel_path: Path, limit: int | None = None) -> List[Tuple[str, str]]:
    """
    Extract danh sách hyperlinks từ file Excel.
    
    Args:
        excel_path: Đường dẫn file Excel
        limit: Số lượng link tối đa (None = tất cả)
        
    Returns:
        List các tuple (display_text, url)
    """
    wb = load_workbook(excel_path)
    ws = wb.active
    
    link_col = find_link_column(ws)
    if not link_col:
        raise ValueError("Không tìm thấy cột Link trong file Excel")
    
    links: List[Tuple[str, str]] = []
    header_row = 2
    
    for row in range(header_row + 1, ws.max_row + 1):
        if limit and len(links) >= limit:
            break
            
        cell = ws.cell(row=row, column=link_col)
        if cell.hyperlink and cell.hyperlink.target:
            display_text = str(cell.value) if cell.value else ""
            url = cell.hyperlink.target
            links.append((display_text, url))
    
    wb.close()
    return links

