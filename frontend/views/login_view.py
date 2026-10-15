"""Refined healthcare SaaS login view for Manas Setu."""

import streamlit as st
from api_client import APIError, ManasSetuClient
from theme import get_bridge_svg, render_helpline_banner


def render_login_view(client: ManasSetuClient) -> None:
    """Render a balanced, intentional two-column sign-in composition."""

    left_col, right_col = st.columns([1.15, 1], gap="large")

    # ── Left Column: Brand Identity & Trust ───────────────────────────
    with left_col:
        st.markdown(
            """
            <div class="ms-brand-badge">
                Smart India Hackathon 2026 • SIH26094
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Bridge-inspired SVG illustration
        st.markdown(get_bridge_svg(), unsafe_allow_html=True)

        st.markdown(
            """
            <div style="margin-bottom: 12px;">
                <h1 class="ms-brand-title">
                    Manas Setu <span class="ms-brand-hindi">मानस सेतु</span>
                </h1>
                <p class="ms-brand-tagline">
                    A bridge to care, dignity, and recovery.
                </p>
                <p class="ms-brand-desc">
                    A privacy-preserving, trauma-informed digital platform connecting victims
                    of atrocities and severe distress to human-supervised mental health monitoring,
                    early crisis detection, and coordinated support services.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Core Human-Centered Highlights
        st.markdown(
            """
            <div style="margin-bottom: 12px;">
                <div class="ms-feature-item">
                    <div class="ms-feature-icon">🛡️</div>
                    <div class="ms-feature-text">
                        <strong>Trauma-Informed Care:</strong> Thoughtfully phrased, nonjudgmental check-ins designed to avoid re-traumatization.
                    </div>
                </div>
                <div class="ms-feature-item">
                    <div class="ms-feature-icon">🔒</div>
                    <div class="ms-feature-text">
                        <strong>DPDP Consent Governance:</strong> Continuous patient agency with instant pause and revoke controls over data processing.
                    </div>
                </div>
                <div class="ms-feature-item">
                    <div class="ms-feature-icon">🤝</div>
                    <div class="ms-feature-text">
                        <strong>Human-Supervised Triage:</strong> AI indicators assist trained caseworkers for early distress intervention without autonomous diagnoses.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Restrained Helplines Panel
        render_helpline_banner()

    # ── Right Column: Refined Sign-In Card ────────────────────────────
    with right_col:
        with st.container(border=True):
            st.markdown(
                """
                <div style="margin-bottom: 14px;">
                    <h3 style="font-size: 1.25rem; font-weight: 700; color: #0f4c5c; margin: 0 0 4px 0;">
                        Sign In to Your Portal
                    </h3>
                    <p style="font-size: 0.85rem; color: #64748b; margin: 0;">
                        Enter your confidential credentials to access your support dashboard.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("login_form", clear_on_submit=False, border=False):
                username = st.text_input(
                    "Username",
                    placeholder="e.g. testvictim or testadmin",
                    help="Your confidential portal account identifier.",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your account password",
                    help="Your account password.",
                )
                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button(
                    "Sign In to Manas Setu →",
                    use_container_width=True,
                    type="primary",
                )

            if submitted:
                if not username.strip() or not password.strip():
                    st.error("Please provide both your username and password.")
                else:
                    with st.spinner("Connecting securely..."):
                        try:
                            token_resp = client.login(username.strip(), password.strip())
                            access_token = token_resp["access_token"]
                            user_resp = client.get_me(access_token)

                            st.session_state.token = access_token
                            st.session_state.user = user_resp
                            st.session_state.current_case_id = None
                            st.session_state.current_nav = "Overview"
                            st.rerun()

                        except APIError as e:
                            if e.status_code == 401:
                                st.error("Incorrect username or password. Please verify your credentials.")
                            elif e.status_code == 503:
                                st.error(f"Cannot connect to the backend server. {e.message}")
                            else:
                                st.error(f"Authentication failed: {e.message}")
                        except Exception as exc:
                            st.error(f"An unexpected error occurred: {exc}")

            # Visually Secondary Collapsible Demonstration Guidance
            with st.expander("🔑 Demonstration Access (Pre-configured)"):
                st.caption(
                    "For jury and evaluation walkthroughs, sample accounts are pre-seeded:\n\n"
                    "• **Victim Portal**: Username `testvictim` | Password `TestPass123!`\n"
                    "  *(Check-ins, consent pause/resume, referrals, safe contacts)*\n\n"
                    "• **Caseworker Portal**: Username `testadmin` | Password `AdminPass123!`\n"
                    "  *(Alert triage queue, alert assignment, referral coordination, audit trail)*"
                )

        # Compact Disclosures Footer
        st.markdown(
            """
            <div style="text-align: center; margin-top: 10px; font-size: 0.76rem; color: #64748b; line-height: 1.45;">
                🔒 <strong>DPDP Act 2023 Compliant</strong> • Cryptographic audit logging enabled.<br>
                🛡️ <strong>Decision-Support Only</strong>: AI models assist clinicians and do not replace professional care.
            </div>
            """,
            unsafe_allow_html=True,
        )
