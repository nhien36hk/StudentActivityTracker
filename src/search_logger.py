"""
Search logger for analytics.
Logs each search query with timestamp and result count.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

LOGS_FILE = Path(__file__).parent.parent / "data" / "search_logs.json"


def log_search(query: str, result_count: int, search_type: Optional[str] = None) -> None:
    """
    Log a search query for analytics.
    
    Args:
        query: Search query string
        result_count: Number of results found
        search_type: 'mssv' or 'name' (auto-detected if None)
    """
    # Determine search type
    if search_type is None:
        search_type = 'mssv' if any(c.isdigit() for c in query) else 'name'
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'query': query,
        'result_count': result_count,
        'search_type': search_type,
    }
    
    # Load existing logs
    logs = []
    if LOGS_FILE.exists():
        try:
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            logs = []
    
    # Append new log
    logs.append(log_entry)
    
    # Save logs
    LOGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def get_total_searches() -> int:
    """Get total number of searches."""
    if not LOGS_FILE.exists():
        return 0
    try:
        with open(LOGS_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        return len(logs)
    except (json.JSONDecodeError, IOError):
        return 0

