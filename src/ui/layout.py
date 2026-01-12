"""
Layout components: Header, Hero section, Footer, Donate.
"""
import streamlit as st
import base64
from pathlib import Path

GITHUB_URL = "https://github.com/nhien36hk/StudentActivityTracker"
DONATE_IMAGE = Path(__file__).parent.parent.parent / "data" / "donate.jpg"


def render_header() -> None:
    """Render header with logo and Github badge."""
    html = f"""
    <div class="header-wrapper">
        <div class="header-container">
            <div class="logo">
                <span class="logo-icon">🎯</span>
                <span>NRL Tracker</span>
            </div>
            <a href="{GITHUB_URL}" target="_blank" class="github-badge">
                <svg height="18" viewBox="0 0 16 16" width="18" fill="currentColor">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 
                    0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52
                    -.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2
                    -3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82
                    .64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 
                    2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 
                    1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                </svg>
                <span>Star on GitHub</span>
            </a>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_hero() -> None:
    """Render hero section with FREE badge and title."""
    html = """
    <div class="hero-container">
        <div class="hero-icon">🎓</div>
        <div class="free-badge">✨ MIỄN PHÍ 100% - KHÔNG MẤT XU NÀO ✨</div>
        <h1 class="hero-title">Tra cứu Điểm Rèn Luyện</h1>
        <p class="hero-subtitle">
            Tra cứu không giới hạn • Hoàn toàn miễn phí • Không cần đăng ký
        </p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_search_hint() -> None:
    """Render search hint below input."""
    html = """
    <div class="search-hint">
        <span>💡</span>
        <span>Hệ thống tự động nhận diện MSSV hoặc Họ tên</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_footer() -> None:
    """Render footer with Github link and star reminder."""
    html = f"""
    <div class="footer-container">
        <a href="{GITHUB_URL}" target="_blank" class="footer-github">
            <span class="star-icon">⭐</span>
            <span style="color: #1a1a2e; font-weight: 600;">
                Nếu thấy hữu ích, hãy cho mình một Star nhé!
            </span>
        </a>
        <p class="footer-text">
            Made with ❤️ by 
            <a href="{GITHUB_URL}" target="_blank" class="footer-link">nhien36hk</a>
            • NRL Tracker v1.0
        </p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def _load_donate_image() -> str:
    """Load và encode donate image thành base64."""
    if not DONATE_IMAGE.exists():
        return ""
    
    with open(DONATE_IMAGE, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_donate() -> None:
    """Render donate section với QR code."""
    img_base64 = _load_donate_image()
    if not img_base64:
        return
    
    html = f"""
    <div class="donate-container">
        <details class="donate-details">
            <summary class="donate-trigger">
                <span class="coffee-icon">🧋</span>
                <span>Mời tôi ly cà phê</span>
            </summary>
            <div class="donate-content">
                <p class="donate-text">
                    Nếu công cụ này giúp ích cho bạn, hãy ủng hộ mình một ly cà phê nhé! 💕
                </p>
                <img src="data:image/jpeg;base64,{img_base64}" 
                     alt="Donate QR Code" 
                     class="donate-qr"/>
                <p class="donate-note">Quét mã QR bằng app ngân hàng</p>
            </div>
        </details>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

