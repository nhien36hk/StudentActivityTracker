"""
Module parse file Word để trích xuất thông tin sinh viên.
"""
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re
from docx import Document


def extract_activity_name_from_filename(file_path: Path) -> str:
    """
    Trích xuất tên chương trình từ tên file.
    
    Tên file format: "001_QĐxx24 - CÔNG NHẬN NRL WORKSHOP XYZ.docx"
    → Lấy phần sau "NRL " hoặc sau " - "
    
    Args:
        file_path: Path của file
        
    Returns:
        Tên chương trình
    """
    filename = file_path.stem  # Bỏ .docx
    
    # Bỏ prefix số (001_, 002_, ...)
    name = re.sub(r'^\d+_', '', filename)
    
    # Bỏ prefix QĐxx24/QĐxx25 và " - "
    name = re.sub(r'^QĐxx\d+\s*-\s*', '', name, flags=re.IGNORECASE)
    
    # Bỏ "CÔNG NHẬN NRL" hoặc "Công nhận NRL"
    name = re.sub(r'^(CÔNG NHẬN|Công nhận)\s+NRL\s*', '', name, flags=re.IGNORECASE)
    
    # Clean up
    name = name.strip()
    name = re.sub(r'\s+', ' ', name)
    
    return name if name else "Unknown"

def find_student_table(doc: Document) -> Optional[object]:
    """
    Tìm bảng chứa danh sách sinh viên.
    Bảng sinh viên cần có: Họ tên + (MSSV hoặc NRL/Điểm).
    Không bắt buộc phải có MSSV (một số file chỉ có Họ tên + Trường + Điểm).
    
    Args:
        doc: Document object
        
    Returns:
        Table object hoặc None
    """
    best_table = None
    best_score = 0
    
    for table in doc.tables:
        if len(table.rows) < 2:
            continue
            
        # Lấy header (dòng đầu tiên)
        header_cells = [cell.text.lower().strip() for cell in table.rows[0].cells]
        header_text = " ".join(header_cells)
        
        # Tính điểm cho mỗi bảng
        score = 0
        has_name = 'họ' in header_text or 'tên' in header_text
        has_mssv = 'mssv' in header_text or 'mã sv' in header_text
        has_nrl = 'nrl' in header_text or 'điểm' in header_text
        has_stt = 'stt' in header_text
        
        if has_name:
            score += 3
        if has_mssv:
            score += 2
        if has_nrl:
            score += 2
        if has_stt:
            score += 1
        
        # Cần ít nhất có Họ tên + (MSSV hoặc NRL)
        if has_name and (has_mssv or has_nrl) and score > best_score:
            best_score = score
            best_table = table
    
    return best_table


def detect_column_indices(header_row) -> Dict[str, int]:
    """
    Xác định vị trí các cột trong header.
    
    Args:
        header_row: Row object của header
        
    Returns:
        Dict mapping tên cột -> index
    """
    indices = {
        'stt': -1,
        'name': -1,
        'student_id': -1,
        'student_class': -1,
        'score': -1,
    }
    
    for idx, cell in enumerate(header_row.cells):
        text = cell.text.lower().strip()
        
        if 'stt' in text:
            indices['stt'] = idx
        elif 'mssv' in text or 'mã sv' in text or 'mã sinh viên' in text:
            indices['student_id'] = idx
        elif 'họ' in text and 'tên' in text:
            indices['name'] = idx
        elif 'lớp' in text or 'trường' in text:
            indices['student_class'] = idx
        elif 'nrl' in text or 'điểm' in text or 'số nrl' in text:
            indices['score'] = idx
    
    return indices


def parse_score(score_text: str) -> float:
    """
    Parse điểm NRL từ text.
    
    Args:
        score_text: Text chứa điểm
        
    Returns:
        Điểm dạng float
    """
    if not score_text:
        return 0.0
    
    # Làm sạch text
    clean_text = score_text.strip().replace(',', '.')
    
    # Tìm số đầu tiên
    match = re.search(r'(\d+\.?\d*)', clean_text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return 0.0
    
    return 0.0


def parse_stt(stt_text: str) -> int:
    """
    Parse số thứ tự từ text.
    
    Args:
        stt_text: Text chứa STT
        
    Returns:
        STT dạng int, 0 nếu không parse được
    """
    if not stt_text:
        return 0
    
    # Tìm số nguyên
    match = re.search(r'(\d+)', stt_text.strip())
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return 0
    
    return 0


def clean_student_id(raw_id: str) -> str:
    """
    Làm sạch MSSV: viết hoa, bỏ khoảng trắng.
    
    Args:
        raw_id: MSSV gốc
        
    Returns:
        MSSV đã làm sạch
    """
    if not raw_id:
        return ""
    return raw_id.strip().upper().replace(" ", "")


def is_student_id(value: str) -> bool:
    """
    Kiểm tra xem giá trị có phải MSSV không.
    MSSV thường là chuỗi số (ví dụ: 2254810315).
    
    Args:
        value: Giá trị cần kiểm tra
        
    Returns:
        True nếu là MSSV
    """
    clean_val = value.strip().replace(" ", "")
    return clean_val.isdigit() and len(clean_val) >= 8


def is_class_code(value: str) -> bool:
    """
    Kiểm tra xem giá trị có phải mã lớp không.
    Mã lớp thường có dạng: 22ĐHTT02, 23ĐHNL04, 21CĐTM 02.
    
    Args:
        value: Giá trị cần kiểm tra
        
    Returns:
        True nếu là mã lớp
    """
    # Loại bỏ space và uppercase
    clean_val = value.strip().replace(' ', '').upper()
    # Pattern: 2 số + chữ (có thể có Đ) + số
    return bool(re.match(r'^\d{2}[A-ZĐÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ]+\d*$', clean_val))


def smart_swap_id_class(raw_id: str, raw_class: str) -> tuple:
    """
    Kiểm tra và swap student_id/student_class nếu bị đảo.
    
    Args:
        raw_id: Giá trị từ cột MSSV
        raw_class: Giá trị từ cột Lớp
        
    Returns:
        Tuple (student_id, student_class) đã được sắp xếp đúng
    """
    raw_id = raw_id.strip()
    raw_class = raw_class.strip()
    
    # Case 1: raw_id là class code và raw_class là student id → swap
    if is_class_code(raw_id) and is_student_id(raw_class):
        return raw_class, raw_id
    
    # Case 2: raw_id rỗng nhưng raw_class là student id → swap
    if not raw_id and is_student_id(raw_class):
        return raw_class, ""
    
    # Case 3: raw_id rỗng nhưng raw_class là class code → giữ nguyên (cả 2 đều không có MSSV)
    # Case 4: raw_class rỗng nhưng raw_id là class code → đây là class, không có MSSV
    if is_class_code(raw_id) and not raw_class:
        return "", raw_id
    
    # Giữ nguyên
    return raw_id, raw_class


def parse_student_table(table, column_indices: Dict[str, int]) -> List[Dict]:
    """
    Parse bảng sinh viên thành list dict.
    Tự động phát hiện và swap MSSV/Lớp cho từng dòng nếu bị đảo.
    
    Args:
        table: Table object
        column_indices: Vị trí các cột
        
    Returns:
        List các dict thông tin sinh viên
    """
    students = []
    id_col = column_indices['student_id']
    class_col = column_indices['student_class']
    
    # Bỏ qua header (dòng 0)
    for row in table.rows[1:]:
        cells = row.cells
        
        # Lấy STT
        stt_text = cells[column_indices['stt']].text.strip() if column_indices['stt'] >= 0 else ""
        stt = parse_stt(stt_text)
        
        # Lấy giá trị các cột
        name = cells[column_indices['name']].text.strip() if column_indices['name'] >= 0 else ""
        raw_id = cells[id_col].text if id_col >= 0 else ""
        raw_class = cells[class_col].text if class_col >= 0 else ""
        score_text = cells[column_indices['score']].text if column_indices['score'] >= 0 else "0"
        
        # Smart swap: kiểm tra từng dòng
        student_id, student_class = smart_swap_id_class(raw_id, raw_class)
        
        # Clean student_id
        student_id = clean_student_id(student_id)
        student_class = student_class.strip()
        
        # Bỏ qua dòng hoàn toàn trống (cả name và student_id đều rỗng)
        if not student_id and not name:
            continue
        
        # Đánh dấu Unknown nếu thiếu thông tin
        if not name:
            name = "UNKNOWN_NAME"
        if not student_id:
            student_id = f"UNKNOWN_ID_{stt}" if stt > 0 else "UNKNOWN_ID"
        if not student_class:
            student_class = "UNKNOWN_CLASS"
        
        students.append({
            'stt': stt,
            'name': name,
            'student_id': student_id,
            'student_class': student_class,
            'score': parse_score(score_text),
        })
    
    return students


def parse_docx_file(file_path: Path, activity_link: str) -> Tuple[str, List[Dict]]:
    """
    Parse file Word, trả về tên chương trình và danh sách sinh viên.
    
    Args:
        file_path: Đường dẫn file .docx
        activity_link: Link gốc của chương trình
        
    Returns:
        Tuple (tên chương trình, list sinh viên với đầy đủ thông tin)
    """
    doc = Document(file_path)
    
    # 1. Lấy tên chương trình từ tên file (đơn giản và chính xác hơn)
    activity_name = extract_activity_name_from_filename(file_path)
    
    # 2. Tìm bảng sinh viên
    table = find_student_table(doc)
    if not table:
        return activity_name, []
    
    # 3. Xác định vị trí cột
    column_indices = detect_column_indices(table.rows[0])
    
    # 4. Parse bảng
    students = parse_student_table(table, column_indices)
    
    # 5. Gắn thêm thông tin activity vào mỗi sinh viên
    for student in students:
        student['activity_name'] = activity_name
        student['activity_link'] = activity_link
    
    return activity_name, students

