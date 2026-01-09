"""
Module gom nhóm dữ liệu sinh viên theo MSSV sử dụng Pandas.
"""
from pathlib import Path
from typing import Dict
import json
import pandas as pd


def load_to_dataframe(json_path: Path) -> pd.DataFrame:
    """
    Load JSON và flatten thành DataFrame.
    
    Args:
        json_path: Đường dẫn file JSON
        
    Returns:
        DataFrame với mỗi dòng là 1 sinh viên trong 1 hoạt động
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        activities = json.load(f)
    
    # Flatten: mỗi student trong mỗi activity thành 1 row
    all_students = []
    for activity in activities:
        all_students.extend(activity.get('students', []))
    
    return pd.DataFrame(all_students)


def aggregate_by_student(df: pd.DataFrame) -> Dict[str, Dict]:
    """
    Gom nhóm theo student_id, tính tổng điểm.
    
    Args:
        df: DataFrame sinh viên
        
    Returns:
        Dict với key là MSSV
    """
    # Group by student_id
    grouped = df.groupby('student_id').agg({
        'name': 'first',
        'student_class': 'first',
        'score': ['sum', 'count'],
    }).reset_index()
    
    # Flatten column names
    grouped.columns = ['student_id', 'name', 'student_class', 'total_score', 'activity_count']
    grouped['total_score'] = grouped['total_score'].round(1)
    
    # Build history cho mỗi sinh viên
    result = {}
    for _, row in grouped.iterrows():
        student_id = row['student_id']
        
        # Lấy history từ df gốc
        history = df[df['student_id'] == student_id][
            ['stt', 'activity_name', 'score', 'activity_link']
        ].to_dict('records')
        
        result[student_id] = {
            'info': {
                'name': row['name'],
                'student_class': row['student_class'],
            },
            'stats': {
                'total_score': row['total_score'],
                'activity_count': int(row['activity_count']),
            },
            'history': history
        }
    
    return result


def save_json(data: Dict, output_path: Path) -> None:
    """Lưu dict ra file JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_summary(df: pd.DataFrame, result: Dict) -> None:
    """In tổng kết."""
    print(f"\n📊 TỔNG KẾT:")
    print(f"   - Tổng records: {len(df)}")
    print(f"   - Sinh viên unique: {len(result)}")
    
    # Top 5
    top5 = sorted(result.items(), key=lambda x: x[1]['stats']['total_score'], reverse=True)[:5]
    print(f"\n🏆 TOP 5 ĐIỂM CAO NHẤT:")
    for i, (sid, data) in enumerate(top5, 1):
        print(f"   {i}. {data['info']['name']} ({sid}) - {data['stats']['total_score']} NRL")

