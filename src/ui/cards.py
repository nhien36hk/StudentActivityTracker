"""
Card components: Student info card, Activity list.
"""
import streamlit as st
from typing import Dict, List


def render_student_card(student_id: str, data: Dict) -> None:
    """
    Render student info card with score badge.
    
    Args:
        student_id: MSSV
        data: Student data dict with info, stats, history
    """
    info = data.get('info', {})
    stats = data.get('stats', {})
    
    name = info.get('name', 'N/A')
    student_class = info.get('student_class', 'N/A')
    total_score = stats.get('total_score', 0)
    activity_count = stats.get('activity_count', 0)
    
    html = f"""
    <div class="student-card">
        <div class="student-header">
            <div class="student-avatar">👤</div>
            <div class="score-badge">
                <div class="score-label">Tổng NRL</div>
                <div class="score-value">{total_score}</div>
            </div>
        </div>
        <div class="student-info">
            <div class="info-row">
                <span>👤</span>
                <strong>{name}</strong>
            </div>
            <div class="info-row">
                <span>🎓</span>
                <span>MSSV: <strong>{student_id}</strong></span>
            </div>
            <div class="info-row">
                <span>📚</span>
                <span>Lớp: <strong>{student_class}</strong></span>
            </div>
            <div class="info-row">
                <span>📋</span>
                <span>Số hoạt động: <strong>{activity_count}</strong></span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_activity_list(history: List[Dict]) -> None:
    """
    Render list of activities.
    
    Args:
        history: List of activity dicts
    """
    if not history:
        return
    
    # Section title
    html_title = """
    <div class="activity-section">
        <div class="activity-title">
            <span>📋</span>
            <span>Chương trình tham gia</span>
        </div>
    </div>
    """
    st.markdown(html_title, unsafe_allow_html=True)
    
    # Render each activity
    for activity in history:
        activity_name = activity.get('activity_name', 'N/A')
        score = activity.get('score', 0)
        link = activity.get('activity_link', '#')
        stt = activity.get('stt', 0)
        
        html_item = f"""
        <div class="activity-item">
            <div class="activity-name">{activity_name}</div>
            <div class="activity-meta">
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <span class="activity-stt">STT: {stt}</span>
                    <span class="activity-score">{score} NRL</span>
                </div>
                <a href="{link}" target="_blank" class="activity-link">
                    <span>Link NRL</span>
                    <span>↗</span>
                </a>
            </div>
        </div>
        """
        st.markdown(html_item, unsafe_allow_html=True)


def render_no_result(query: str) -> None:
    """
    Render no result message.
    
    Args:
        query: Search query that had no results
    """
    html = f"""
    <div class="no-result">
        <div class="no-result-icon">🔍</div>
        <div class="no-result-text">
            Không tìm thấy kết quả cho <strong>"{query}"</strong>
            <br><br>
            <small>Hãy kiểm tra lại MSSV hoặc họ tên của bạn</small>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

