"""
Update Banner component - Big announcement for data updates.
"""
import streamlit as st


def render_update_banner() -> None:
    """Render the big update announcement banner."""
    html = """
    <div class="update-banner">
        <div class="banner-glow"></div>
        <div class="banner-content">
            <div class="banner-badge">🔥 BIG UPDATE</div>
            <div class="banner-title">
                <span class="highlight">FULL DATA 2023 - 2025</span>
            </div>
            <div class="banner-stats">
                <div class="stat-divider">•</div>
                <div class="stat-item">
                    <span class="stat-icon">✨</span>
                    <span class="stat-text"><strong>+1,448</strong> mới</span>
                </div>
                <div class="stat-divider">•</div>
                <div class="stat-item">
                    <span class="stat-icon">🔄</span>
                    <span class="stat-text"><strong>3,384</strong> cập nhật</span>
                </div>
                    <div class="stat-item stat-total">
                    <span class="stat-icon">👥</span>
                    <span class="stat-text"><strong>8,684</strong> sinh viên</span>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

