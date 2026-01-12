"""
NRL Tracker - Main Streamlit Application.
Controller file that orchestrates UI components and logic.
"""
import streamlit as st
from pathlib import Path

from src.ui.layout import render_header, render_hero, render_footer, render_search_hint, render_donate
from src.ui.cards import render_student_card, render_activity_list, render_no_result
from src.ui.banner import render_update_banner
from src.searcher import search_student
from src.search_logger import log_search

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="NRL Tracker - Tra cứu Ngày rèn luyện",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============ LOAD CSS ============
def load_css() -> None:
    """Inject CSS from external file."""
    css_file = Path(__file__).parent / "src" / "ui" / "styles.css"
    with open(css_file, 'r', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


load_css()


# ============ RENDER UI ============
render_header()
# render_update_banner()
render_hero()

# Search box - using columns (CSS targets stHorizontalBlock)
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        label="Tìm kiếm",
        placeholder="Nhập MSSV (VD: 22130001) hoặc Họ tên (VD: Nguyễn Văn A)",
        label_visibility="collapsed",
    )
with col2:
    search_clicked = st.button("🔍 Tìm kiếm")

render_search_hint()


# ============ SEARCH LOGIC ============
if query and (search_clicked or query):
    results = search_student(query)
    
    # Log search
    log_search(query, len(results))
    
    # Results container
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    if results:
        # Show results
        for mssv, student_data in results:
            render_student_card(mssv, student_data)
            
            history = student_data.get('history', [])
            if history:
                render_activity_list(history)
            
            # Separator between multiple results
            if len(results) > 1:
                st.markdown("<hr style='margin: 2rem 0; border-color: #e8eef5;'>", 
                           unsafe_allow_html=True)
    else:
        render_no_result(query)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============ FOOTER ============
render_donate()
render_footer()

