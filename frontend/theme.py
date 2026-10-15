"""Manas Setu Theme & Visual Design System.

Provides consistent healthcare SaaS styling:
- Deep teal (#0f4c5c / #134e4a) and muted sage (#52796f / #475569) palette.
- Warm off-white background (#f8faf9 / #fbfcfb).
- Clean card borders, rounded corners (12px), subtle shadows.
- Accessible, non-stigmatizing badges and indicators.
- Offline SVG bridge-inspired visual identity.
"""

import streamlit as st


CUSTOM_CSS = """
<style>
/* Global App Canvas */
.stApp {
    background-color: #f8faf9;
    color: #1e293b;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Hide default streamlit decorations */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Refined Container Spacing - Breathable and Balanced */
.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 2rem !important;
    max-width: 1140px !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}

/* Distinctive Brand Headers */
.ms-brand-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #f0fdfa;
    border: 1px solid #ccfbf1;
    color: #0f766e;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 9999px;
    margin-bottom: 8px;
}

.ms-brand-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #0f4c5c;
    margin: 0 0 4px 0;
    letter-spacing: -0.02em;
    line-height: 1.15;
}

.ms-brand-hindi {
    font-size: 1.2rem;
    font-weight: 600;
    color: #52796f;
    margin-left: 8px;
}

.ms-brand-tagline {
    font-size: 1rem;
    color: #334155;
    font-weight: 500;
    margin: 0 0 8px 0;
    line-height: 1.4;
}

.ms-brand-desc {
    font-size: 0.88rem;
    color: #64748b;
    margin: 0 0 16px 0;
    line-height: 1.55;
}

/* Feature Bullets (Hero left side) */
.ms-feature-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 10px;
}

.ms-feature-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 6px;
    background: #f0fdfa;
    border: 1px solid #ccfbf1;
    color: #0f766e;
    font-size: 0.9rem;
    flex-shrink: 0;
}

.ms-feature-text {
    font-size: 0.84rem;
    color: #475569;
    line-height: 1.4;
}

.ms-feature-text strong {
    color: #0f172a;
    font-weight: 600;
}

/* Card Container */
.ms-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.ms-login-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 24px 28px;
    box-shadow: 0 4px 20px -2px rgba(15, 76, 92, 0.08);
}

/* Streamlit Container / Border Wrappers */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-color: #e2e8f0 !important;
    border-radius: 12px !important;
    background-color: #ffffff !important;
    box-shadow: 0 4px 16px -2px rgba(15, 76, 92, 0.06) !important;
}

.ms-card-compact {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.ms-card-interactive:hover {
    border-color: #cbd5e1;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.06);
}

/* Metric Card */
.ms-stat-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 18px;
    text-align: left;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.ms-stat-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
    margin-bottom: 4px;
}

.ms-stat-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #0f4c5c;
    margin: 0;
    line-height: 1.1;
}

.ms-stat-desc {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 4px;
}

/* Status Badges */
.ms-badge {
    display: inline-block;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 9999px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.ms-badge-routine, .ms-badge-granted, .ms-badge-completed {
    background-color: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
}

.ms-badge-follow_up, .ms-badge-paused, .ms-badge-in_progress, .ms-badge-assigned {
    background-color: #fffbeb;
    color: #92400e;
    border: 1px solid #fde68a;
}

.ms-badge-urgent, .ms-badge-withdrawn, .ms-badge-escalated {
    background-color: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
}

.ms-badge-neutral, .ms-badge-created, .ms-badge-acknowledged {
    background-color: #f1f5f9;
    color: #334155;
    border: 1px solid #cbd5e1;
}

/* Primary Hero Banner */
.ms-hero-banner {
    background: linear-gradient(135deg, #0f4c5c 0%, #1c6e7d 100%);
    color: #ffffff;
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(15, 76, 92, 0.12);
}

.ms-hero-title {
    font-size: 1.4rem;
    font-weight: 700;
    margin: 0 0 6px 0;
    color: #ffffff;
}

.ms-hero-subtitle {
    font-size: 0.92rem;
    color: #e0f2fe;
    margin: 0;
    line-height: 1.4;
}

/* Refined Helpline Panel */
.ms-helpline-panel {
    background-color: #f0fdfa;
    border: 1px solid #ccfbf1;
    border-left: 4px solid #0f766e;
    border-radius: 10px;
    padding: 10px 14px;
    margin-top: 14px;
}

.ms-helpline-header {
    font-size: 0.8rem;
    font-weight: 700;
    color: #0f766e;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 3px;
}

.ms-helpline-body {
    font-size: 0.82rem;
    color: #334155;
    line-height: 1.45;
}

/* Empty State */
.ms-empty-state {
    text-align: center;
    padding: 32px 20px;
    color: #64748b;
    border: 1px dashed #cbd5e1;
    border-radius: 12px;
    background: #ffffff;
    margin: 14px 0;
}

.ms-empty-icon {
    font-size: 2rem;
    margin-bottom: 6px;
}

/* All Primary Buttons: form submit buttons, standard primary buttons, baseButton-primary */
button[kind="primary"],
button[data-testid="baseButton-primary"],
div[data-testid="stFormSubmitButton"] > button,
div.stFormSubmitButton > button,
div.stButton > button[kind="primary"] {
    background-color: #0f4c5c !important;
    border-color: #0f4c5c !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 9px 18px !important;
    font-size: 0.95rem !important;
    transition: all 0.15s ease-in-out !important;
    box-shadow: 0 1px 3px rgba(15, 76, 92, 0.18) !important;
}

button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
div.stFormSubmitButton > button:hover,
div.stButton > button[kind="primary"]:hover {
    background-color: #0a3642 !important;
    border-color: #0a3642 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 6px -1px rgba(15, 76, 92, 0.28) !important;
}

button[kind="primary"]:focus,
button[kind="primary"]:active,
button[data-testid="baseButton-primary"]:focus,
div[data-testid="stFormSubmitButton"] > button:focus {
    background-color: #0a3642 !important;
    border-color: #0a3642 !important;
    box-shadow: 0 0 0 3px rgba(15, 76, 92, 0.25) !important;
    outline: none !important;
}

button[kind="secondary"] {
    border-radius: 8px !important;
    border: 1px solid #cbd5e1 !important;
    color: #334155 !important;
    background-color: #ffffff !important;
    font-weight: 500 !important;
}

button[kind="secondary"]:hover {
    border-color: #94a3b8 !important;
    background-color: #f8fafc !important;
    color: #0f4c5c !important;
}

/* High-Contrast Field Labels */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
.stTextInput label,
.stTextInput label p,
.stTextArea label,
.stTextArea label p,
.stSelectbox label,
.stSelectbox label p {
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    color: #0f172a !important;
    margin-bottom: 2px !important;
}

/* Input Fields - Clean High-Contrast Borders & Text */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stTextArea > div > div > textarea {
    border-radius: 8px !important;
    border: 1.5px solid #94a3b8 !important;
    font-size: 0.92rem !important;
    color: #0f172a !important;
    background-color: #ffffff !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

/* Clear Focus State with Teal Glow */
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > div:focus-within {
    border-color: #0f4c5c !important;
    box-shadow: 0 0 0 3px rgba(15, 76, 92, 0.2) !important;
    outline: none !important;
}

/* Accessible Placeholder Contrast */
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #f1f5f9;
    border-right: 1px solid #e2e8f0;
}
</style>
"""


def get_bridge_svg() -> str:
    """Return inline SVG representing the Manas Setu bridge motif.

    Visualizes a supportive bridge connecting two banks (distress to recovery)
    with a central beacon representing human care and AI decision support.
    """
    return """
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
    <svg viewBox="0 0 340 76" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%; max-width: 290px; height: auto;">
      <defs>
        <linearGradient id="bridgeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#0f4c5c" />
          <stop offset="50%" stop-color="#14b8a6" />
          <stop offset="100%" stop-color="#52796f" />
        </linearGradient>
      </defs>
      <!-- Suspension Arch -->
      <path d="M10 62 C 80 18, 260 18, 330 62" stroke="url(#bridgeGradient)" stroke-width="3.5" stroke-linecap="round" fill="none"/>
      <path d="M25 62 C 95 30, 245 30, 315 62" stroke="#a7f3d0" stroke-width="1.8" stroke-linecap="round" fill="none" opacity="0.8"/>
      <!-- Deck / Roadway -->
      <line x1="8" y1="62" x2="332" y2="62" stroke="#0f4c5c" stroke-width="2.5" stroke-linecap="round"/>
      <!-- Vertical Support Cables -->
      <line x1="75" y1="43" x2="75" y2="62" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="2 2"/>
      <line x1="120" y1="31" x2="120" y2="62" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="2 2"/>
      <line x1="170" y1="26" x2="170" y2="62" stroke="#0f4c5c" stroke-width="2"/>
      <line x1="220" y1="31" x2="220" y2="62" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="2 2"/>
      <line x1="265" y1="43" x2="265" y2="62" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="2 2"/>
      <!-- Central Beacon of Care -->
      <circle cx="170" cy="25" r="5" fill="#0f4c5c"/>
      <circle cx="170" cy="25" r="2.5" fill="#ffffff"/>
      <circle cx="170" cy="25" r="9" stroke="#14b8a6" stroke-width="1.2" opacity="0.6"/>
    </svg>
    </div>
    """


def apply_theme() -> None:
    """Inject custom healthcare design CSS into the current Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_badge(status_or_risk: str, text: str | None = None) -> str:
    """Generate an HTML badge string for status or risk level."""
    normalized = str(status_or_risk).lower().strip().replace(" ", "_")
    label = text or status_or_risk.capitalize()

    css_class = "ms-badge-neutral"
    if normalized in ("routine", "granted", "completed", "low"):
        css_class = "ms-badge-routine"
    elif normalized in ("follow_up", "paused", "in_progress", "assigned", "moderate", "high"):
        css_class = "ms-badge-follow_up"
    elif normalized in ("urgent", "withdrawn", "escalated"):
        css_class = "ms-badge-urgent"

    return f'<span class="ms-badge {css_class}">{label}</span>'



def render_helpline_banner() -> None:
    """Render a restrained, accessible support panel for verified emergency helplines."""
    st.markdown(
        """
        <div class="ms-helpline-panel">
            <div class="ms-helpline-header">🛡️ 24/7 Verified Emergency Helplines (India)</div>
            <div class="ms-helpline-body">
                • <strong>Tele-MANAS (Mental Health):</strong> 14416 / 1800-891-4416 (Toll-Free, 20+ Languages)<br>
                • <strong>National Emergency Helpline:</strong> 112 | <strong>Women Helpline:</strong> 1091
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
