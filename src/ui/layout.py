"""
Layout components: Header, Hero section, Footer, Donate.
"""
import streamlit as st
import base64
from pathlib import Path

GITHUB_URL = "https://github.com/nhien36hk/StudentActivityTracker"
DONATE_IMAGE = Path(__file__).parent.parent.parent / "data" / "donate.jpg"


def render_header() -> None:
    """Render header with logo and donate button."""
    img_base64 = _load_donate_image()
    
    html = f"""
    <div class="header-wrapper">
        <div class="header-container">
            <div class="logo">
                <span class="logo-icon">🎯</span>
                <span>NRL Tracker</span>
            </div>
            <label for="donate-modal-toggle" class="header-donate-btn">
                <span class="header-coffee-icon">☕</span>
                <span>Mời tớ ly cà phê</span>
            </label>
        </div>
    </div>
    
    <!-- Popup Modal -->
    <input type="checkbox" id="donate-modal-toggle" class="modal-toggle">
    <div class="modal-overlay">
        <div class="modal-content">
            <label for="donate-modal-toggle" class="modal-close">✕</label>
            <div class="modal-header">
                <span class="modal-icon">☕</span>
                <h3>Ủng hộ tác giả</h3>
            </div>
            <p class="modal-text">
                Nếu công cụ này hữu ích, hãy mời mình ly cà phê nhé! 💕
            </p>
            <img src="data:image/jpeg;base64,{img_base64}" 
                 alt="Donate QR Code" 
                 class="modal-qr"/>
            <p class="modal-note">Quét mã QR bằng app ngân hàng</p>
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
                <span>Mời tớ ly cà phê</span>
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

