"""
Script merge dữ liệu NRL từ nhiều nguồn.

Merge 2 file students.json theo MSSV:
- Nếu MSSV mới → thêm vào
- Nếu MSSV đã có → gộp activities + cộng điểm

Usage:
    python scripts/merge_data.py                           # Merge mặc định
    python scripts/merge_data.py --old data/students.json --new data/students_2023.json
    python scripts/merge_data.py --output data/merged.json
"""
import sys
import argparse
import json
from pathlib import Path

# Thêm parent folder vào sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))


# ============ DEFAULT PATHS ============
DEFAULT_OLD = Path("data/students_merged.json")
DEFAULT_NEW = Path("data/students_new.json")
DEFAULT_OUTPUT = Path("data/students_merged.json")


def load_json(filepath: Path) -> dict:
    """Load JSON file."""
    if not filepath.exists():
        print(f"❌ File không tồn tại: {filepath}")
        return {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: dict, filepath: Path) -> None:
    """Save dict to JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def merge_student_data(old_data: dict, new_data: dict) -> dict:
    """
    Merge 2 dict students theo MSSV.
    
    Logic:
    - MSSV mới → copy nguyên
    - MSSV trùng → gộp history + cộng điểm
    
    Returns:
        dict: Merged data
    """
    merged = old_data.copy()
    
    new_count = 0
    updated_count = 0
    
    for mssv, student in new_data.items():
        if mssv not in merged:
            # MSSV mới - thêm nguyên
            merged[mssv] = student
            new_count += 1
        else:
            # MSSV trùng - merge
            existing = merged[mssv]
            
            # Gộp history (tránh duplicate)
            existing_links = {h['activity_link'] for h in existing.get('history', [])}
            
            for activity in student.get('history', []):
                if activity['activity_link'] not in existing_links:
                    updated_count += 1
                    existing['history'].append(activity)
            
            # Tính lại stats
            total_score = sum(h.get('score', 0) for h in existing['history'])
            existing['stats'] = {
                'total_score': total_score,
                'activity_count': len(existing['history'])
            }
    
    return merged, new_count, updated_count


def print_stats(old_data: dict, new_data: dict, merged: dict, new_count: int, updated_count: int):
    """In thống kê merge."""
    print("\n" + "="*60)
    print("📊 THỐNG KÊ MERGE")
    print("="*60)
    
    print(f"\n📁 File cũ:    {len(old_data):,} sinh viên")
    print(f"📁 File mới:   {len(new_data):,} sinh viên")
    print(f"📁 Sau merge:  {len(merged):,} sinh viên")
    
    print(f"\n✨ Thêm mới:   {new_count:,}")
    print(f"🔄 Cập nhật:   {updated_count:,}")
    
    # Top 5 sinh viên có nhiều điểm nhất
    print("\n🏆 Top 5 sinh viên nhiều điểm nhất:")
    sorted_students = sorted(
        merged.items(), 
        key=lambda x: x[1].get('stats', {}).get('total_score', 0),
        reverse=True
    )[:5]
    
    for i, (mssv, student) in enumerate(sorted_students, 1):
        name = student.get('info', {}).get('name', 'N/A')
        score = student.get('stats', {}).get('total_score', 0)
        activities = student.get('stats', {}).get('activity_count', 0)
        print(f"   {i}. {name[:30]} ({mssv}) - {score} điểm ({activities} HĐ)")


def main():
    parser = argparse.ArgumentParser(
        description="Merge dữ liệu NRL từ nhiều nguồn"
    )
    parser.add_argument(
        '--old', '-o',
        type=Path,
        default=DEFAULT_OLD,
        help=f'File dữ liệu cũ (mặc định: {DEFAULT_OLD})'
    )
    parser.add_argument(
        '--new', '-n',
        type=Path,
        default=DEFAULT_NEW,
        help=f'File dữ liệu mới (mặc định: {DEFAULT_NEW})'
    )
    parser.add_argument(
        '--output', '-out',
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f'File output (mặc định: {DEFAULT_OUTPUT})'
    )
    parser.add_argument(
        '--replace', '-r',
        action='store_true',
        help='Ghi đè file cũ thay vì tạo file mới'
    )
    args = parser.parse_args()
    
    print("🔀 NRL DATA MERGER")
    print("="*60)
    print(f"📂 File cũ:  {args.old}")
    print(f"📂 File mới: {args.new}")
    
    # Load data
    print("\n📖 Đang load dữ liệu...")
    old_data = load_json(args.old)
    new_data = load_json(args.new)
    
    if not old_data:
        print(f"⚠️  File cũ trống hoặc không tồn tại. Sử dụng file mới làm base.")
        old_data = {}
    
    if not new_data:
        print(f"❌ File mới trống hoặc không tồn tại!")
        return
    
    # Merge
    print("\n🔄 Đang merge...")
    merged, new_count, updated_count = merge_student_data(old_data, new_data)
    
    # Stats
    print_stats(old_data, new_data, merged, new_count, updated_count)
    
    # Save
    output_path = args.old if args.replace else args.output
    print(f"\n💾 Lưu kết quả: {output_path}")
    save_json(merged, output_path)
    
    print("\n" + "="*60)
    print("✅ MERGE HOÀN TẤT!")
    print("="*60)
    
    if args.replace:
        print(f"   File {args.old} đã được cập nhật.")
    else:
        print(f"   File mới: {output_path}")
        print(f"\n💡 Để ghi đè file cũ, chạy lại với --replace")


if __name__ == "__main__":
    main()

