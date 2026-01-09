"""
Smart search module: MSSV (hash lookup) or Name (partial match).
"""
import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import streamlit as st


STUDENTS_FILE = Path(__file__).parent.parent / "data" / "students_merged.json"


@st.cache_data
def load_students() -> Dict:
    """Load students data from JSON file with caching."""
    with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def remove_vietnamese_diacritics(text: str) -> str:
    """
    Remove Vietnamese diacritics for flexible matching.
    Example: "Nguyễn Văn Á" -> "nguyen van a"
    """
    # Normalize to decomposed form
    nfkd = unicodedata.normalize('NFKD', text)
    # Remove diacritical marks
    ascii_text = ''.join(c for c in nfkd if not unicodedata.combining(c))
    # Convert đ/Đ
    ascii_text = ascii_text.replace('đ', 'd').replace('Đ', 'D')
    return ascii_text.lower()


def has_digit(text: str) -> bool:
    """Check if text contains any digit."""
    return any(c.isdigit() for c in text)


def search_by_mssv(query: str, data: Dict) -> List[Tuple[str, Dict]]:
    """
    Direct hash lookup by MSSV. O(1) complexity.
    
    Args:
        query: MSSV string
        data: Students dict
    
    Returns:
        List of (mssv, student_data) tuples
    """
    query_upper = query.strip().upper()
    
    # Exact match first
    if query_upper in data:
        return [(query_upper, data[query_upper])]
    
    # Partial match (e.g., "2213" matches all MSSV containing "2213")
    results = []
    for mssv, student_data in data.items():
        if query_upper in mssv.upper():
            results.append((mssv, student_data))
    
    return results[:10]  # Limit results


def search_by_name(query: str, data: Dict) -> List[Tuple[str, Dict]]:
    """
    Partial match by name (case-insensitive, diacritics-insensitive).
    
    Args:
        query: Name string
        data: Students dict
    
    Returns:
        List of (mssv, student_data) tuples
    """
    query_normalized = remove_vietnamese_diacritics(query.strip())
    
    results = []
    for mssv, student_data in data.items():
        info = student_data.get('info', {})
        name = info.get('name', '')
        name_normalized = remove_vietnamese_diacritics(name)
        
        if query_normalized in name_normalized:
            results.append((mssv, student_data))
    
    return results[:10]  # Limit results


def search_student(query: str) -> List[Tuple[str, Dict]]:
    """
    Smart search: auto-detect MSSV vs Name.
    
    - If query contains digits -> search by MSSV
    - If query is text only -> search by name
    
    Args:
        query: Search string
    
    Returns:
        List of (mssv, student_data) tuples
    """
    if not query or not query.strip():
        return []
    
    data = load_students()
    query = query.strip()
    
    if has_digit(query):
        # MSSV search (has numbers)
        return search_by_mssv(query, data)
    else:
        # Name search (no numbers)
        return search_by_name(query, data)



