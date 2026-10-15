"""Manas Setu — Streamlit Frontend Entry Point.

AI-Powered Dynamic Mental Health Monitoring and Distress Prediction System
for Victims of Atrocities (Smart India Hackathon 2026 — Problem Statement SIH26094).
"""

import os
import sys
from pathlib import Path

# Ensure the frontend folder and project root are in sys.path
FRONTEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FRONTEND_DIR.parent
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(1, str(PROJECT_ROOT))

import streamlit as st
from api_client import APIError, ManasSetuClient
from theme import apply_theme, render_badge
from views.login_view import render_login_view
from views.staff_views import render_staff_portal
from views.victim_views import render_victim_portal


VICTIM_PAGES = [
    ("Overview", "🏠"),
    ("Well-being Check-In", "📝"),
    ("My Assessments", "📊"),
    ("Support & Referrals", "🤝"),
    ("Consent & Privacy", "🔒"),
    ("Safe Contacts", "🛡️"),
]

STAFF_PAGES = [
    ("Overview", "🏠"),
    ("Alert Queue", "🚨"),
    ("Case Referrals", "🤝"),
    ("Audit Logs", "📋"),
]


def init_session_state() -> None:
    """Initialize persistent Streamlit session keys."""
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "base_url" not in st.session_state:
        st.session_state.base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    if "current_nav" not in st.session_state:
        st.session_state.current_nav = "Overview"
    if "current_case_id" not in st.session_state:
        st.session_state.current_case_id = None


def render_sidebar(client: ManasSetuClient) -> str:
    """Render the application branding, navigation, and compact user session controls."""
    with st.sidebar:
        # Tasteful Brand Header
        st.markdown(
            """
            <div style="margin-bottom: 20px;">
                <div style="font-size: 1.35rem; font-weight: 800; color: #0f4c5c; line-height: 1.1;">
                    🛡️ Manas Setu
                </div>
                <div style="font-size: 0.85rem; font-weight: 500; color: #64748b; margin-top: 2px;">
                    मानस सेतु • Care & Support
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        user = st.session_state.user
        token = st.session_state.token

        if token and user:
            role = user.get("role", "victim").lower()
            is_staff = role in ("admin", "caseworker", "counsellor")
            pages = STAFF_PAGES if is_staff else VICTIM_PAGES

            st.markdown(
                "<div style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; margin-bottom: 8px;'>Navigation</div>",
                unsafe_allow_html=True,
            )

            # Navigation radio
            page_labels = [p[0] for p in pages]
            page_icons = {p[0]: p[1] for p in pages}

            if st.session_state.current_nav not in page_labels:
                st.session_state.current_nav = page_labels[0]

            selected_page = st.radio(
                "Go to page",
                options=page_labels,
                index=page_labels.index(st.session_state.current_nav),
                format_func=lambda x: f"{page_icons[x]}  {x}",
                label_visibility="collapsed",
                key="sidebar_navigation_radio",
            )
            st.session_state.current_nav = selected_page

            st.markdown("---")

            # Compact Account Card
            role_label = user.get("role", "").capitalize()
            role_badge = render_badge(role, text=role_label)
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px; margin-bottom: 12px;">
                    <div style="font-size: 0.88rem; font-weight: 600; color: #0f4c5c;">{user.get('username')}</div>
                    <div style="margin-top: 4px;">{role_badge}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Sign Out", use_container_width=True, type="secondary"):
                st.session_state.token = None
                st.session_state.user = None
                st.session_state.current_case_id = None
                st.session_state.current_nav = "Overview"
                st.rerun()

        # Connection health pill
        try:
            health = client.check_health()
            if health.get("status") == "healthy":
                st.markdown(
                    "<div style='font-size: 0.75rem; color: #065f46; display: flex; align-items: center; gap: 4px; margin-top: 16px;'>● Backend Connected (Port 8000)</div>",
                    unsafe_allow_html=True,
                )
        except APIError:
            st.markdown(
                "<div style='font-size: 0.75rem; color: #991b1b; display: flex; align-items: center; gap: 4px; margin-top: 16px;'>● Backend Disconnected</div>",
                unsafe_allow_html=True,
            )

        # Discreet Emergency Help
        st.markdown("---")
        st.markdown(
            """
            <div style="font-size: 0.75rem; color: #64748b; line-height: 1.4;">
                <strong style="color: #0f766e;">24/7 Crisis Helplines:</strong><br>
                Tele-MANAS: <strong>14416</strong><br>
                Emergency: <strong>112</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return st.session_state.current_nav


def main() -> None:
    st.set_page_config(
        page_title="Manas Setu | Mental Health Support",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Apply modern healthcare SaaS design system
    apply_theme()

    init_session_state()

    client = ManasSetuClient(base_url=st.session_state.base_url)

    token = st.session_state.token
    user = st.session_state.user

    if not token or not user:
        render_login_view(client)
        return

    # Render authenticated sidebar with active navigation
    active_nav = render_sidebar(client)

    role = user.get("role", "").lower()

    if role == "victim":
        render_victim_portal(client, token, user, active_nav)
    elif role in ("admin", "caseworker", "counsellor"):
        render_staff_portal(client, token, user, active_nav)
    else:
        st.error(f"Unrecognized role: {role}")


if __name__ == "__main__":
    main()
