"""
Script xử lý dữ liệu NRL: Download từ Google Docs → Parse → Aggregate.

Usage:
    python scripts/build_data.py                              # File mặc định
    python scripts/build_data.py --limit 5                    # Test 5 links
    python scripts/build_data.py --excel data/2023-2024.xlsx  # File Excel khác
    
Example:
    python scripts/build_data.py --excel data/2023-2024.xlsx
    # Output tự động: data/students_2023-2024.json
"""
import sys
import argparse
from pathlib import Path

# Thêm parent folder vào sys.path để import src
sys.path.append(str(Path(__file__).resolve().parent.parent))

import json
from src.extractor import extract_hyperlinks
from src.downloader import download_docx, sanitize_filename
from src.parser import parse_docx_file
from src.aggregator import load_to_dataframe, aggregate_by_student, save_json, print_summary


# ============ DEFAULT PATHS ============
DEFAULT_EXCEL = Path("data/danhsachct.xlsx")

# Paths (sẽ được set trong main dựa vào arguments)
EXCEL_PATH = DEFAULT_EXCEL
DOWNLOAD_DIR = Path("data/downloaded")
RAW_OUTPUT = Path("data/raw_activities.json")
FINAL_OUTPUT = Path("data/students.json")


def process_single_link(display_text: str, url: str, index: int) -> dict:
    """Download và parse một link."""
    print(f"\n{'='*60}")
    print(f"📄 [{index}] {display_text[:50]}...")
    
    # Tạo tên file
    filename = sanitize_filename(f"{index:03d}_{display_text}")
    if not filename.endswith('.docx'):
        filename += '.docx'
    file_path = DOWNLOAD_DIR / filename
    
    # Download
    print(f"⬇️  Downloading...")
    success = download_docx(url, file_path)
    
    if not success:
        print(f"❌ Download failed!")
        return {'error': 'Download failed', 'url': url, 'students': []}
    
    # Parse
    print(f"🔍 Parsing...")
    activity_name, students = parse_docx_file(file_path, url)
    
    print(f"✅ {activity_name[:40]}... | {len(students)} sinh viên")
    
    return {
        'activity_name': activity_name,
        'activity_link': url,
        'student_count': len(students),
        'students': students
    }


def step1_download_and_parse(limit: int | None) -> list:
    """Bước 1: Download tất cả files và parse."""
    print("\n" + "="*60)
    print("📥 BƯỚC 1: DOWNLOAD & PARSE")
    print("="*60)
    
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Extract links
    print(f"\n📂 Đọc file Excel: {EXCEL_PATH}")
    links = extract_hyperlinks(EXCEL_PATH, limit=limit)
    total = len(links)
    print(f"✅ Tìm thấy {total} links" + (f" (giới hạn {limit})" if limit else ""))
    
    # Process từng link
    results = []
    for idx, (display_text, url) in enumerate(links, 1):
        result = process_single_link(display_text, url, idx)
        results.append(result)
    
    # Lưu raw data
    print(f"\n💾 Lưu raw data: {RAW_OUTPUT}")
    RAW_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(RAW_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    total_students = sum(r.get('student_count', 0) for r in results)
    print(f"📊 Tổng: {len(results)} chương trình | {total_students} records")
    
    return results


def step2_aggregate(raw_data: list) -> dict:
    """Bước 2: Gom nhóm theo MSSV."""
    print("\n" + "="*60)
    print("🔄 BƯỚC 2: AGGREGATE THEO MSSV")
    print("="*60)
    
    # Flatten students từ raw_data
    all_students = []
    for activity in raw_data:
        all_students.extend(activity.get('students', []))
    
    if not all_students:
        print("⚠️ Không có sinh viên nào!")
        return {}
    
    # Convert to DataFrame và aggregate
    import pandas as pd
    df = pd.DataFrame(all_students)
    print(f"📋 DataFrame: {len(df)} rows")
    
    result = aggregate_by_student(df)
    
    # Summary
    print_summary(df, result)
    
    # Lưu final data
    print(f"\n💾 Lưu final data: {FINAL_OUTPUT}")
    save_json(result, FINAL_OUTPUT)
    
    return result


def main():
    global EXCEL_PATH, DOWNLOAD_DIR, RAW_OUTPUT, FINAL_OUTPUT
    
    parser = argparse.ArgumentParser(
        description="Build NRL data: Download → Parse → Aggregate"
    )
    parser.add_argument(
        '-l', '--limit',
        type=int,
        default=None,
        help='Số lượng links xử lý (mặc định: tất cả)'
    )
    parser.add_argument(
        '-e', '--excel',
        type=Path,
        default=DEFAULT_EXCEL,
        help=f'File Excel input (mặc định: {DEFAULT_EXCEL})'
    )
    args = parser.parse_args()
    
    # Set paths dựa vào file Excel
    EXCEL_PATH = args.excel
    if args.excel != DEFAULT_EXCEL:
        excel_name = args.excel.stem  # e.g. "2023-2024"
        DOWNLOAD_DIR = Path(f"data/downloaded_{excel_name}")
        RAW_OUTPUT = Path(f"data/raw_{excel_name}.json")
        FINAL_OUTPUT = Path(f"data/students_{excel_name}.json")
    
    print("🚀 NRL DATA BUILDER")
    print("="*60)
    print(f"   📂 Excel:  {EXCEL_PATH}")
    print(f"   📂 Output: {FINAL_OUTPUT}")
    print(f"   🔢 Limit:  {args.limit if args.limit else 'ALL'}")
    
    # Bước 1: Download & Parse
    raw_data = step1_download_and_parse(args.limit)
    
    # Bước 2: Aggregate
    final_data = step2_aggregate(raw_data)
    
    # Hoàn tất
    print("\n" + "="*60)
    print("✅ HOÀN TẤT!")
    print("="*60)
    print(f"   📁 Raw data:   {RAW_OUTPUT}")
    print(f"   📁 Final data: {FINAL_OUTPUT}")
    print(f"   👥 Sinh viên:  {len(final_data)}")


if __name__ == "__main__":
    main()

