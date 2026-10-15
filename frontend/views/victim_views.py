"""Redesigned calm, trauma-informed victim portal views for Manas Setu."""

from typing import Any
import streamlit as st
from api_client import APIError, ManasSetuClient
from theme import render_badge, render_helpline_banner


def render_victim_portal(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
    active_nav: str,
) -> None:
    """Main victim portal router dispatching to dedicated sub-views."""

    # 1. Load victim's cases
    try:
        cases = client.get_my_cases(token)
    except APIError as e:
        st.error(f"Unable to load case records: {e.message}")
        return

    # If no case exists, present a welcoming case-setup card
    if not cases:
        st.markdown(
            """
            <div class="ms-card" style="text-align: center; padding: 40px 20px;">
                <h2 style="color: #0f4c5c; margin-bottom: 8px;">Welcome to Your Support Portal</h2>
                <p style="color: #475569; max-width: 600px; margin: 0 auto 24px auto;">
                    To begin confidential distress monitoring and access coordinated support services,
                    please create your secure, anonymized support case.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _, c_btn, _ = st.columns([1, 1.5, 1])
        with c_btn:
            if st.button("➕ Generate My Confidential Support Case", type="primary", use_container_width=True):
                with st.spinner("Setting up your confidential case..."):
                    try:
                        new_case = client.generate_case(token)
                        st.success(f"Case #{new_case['id']} generated successfully!")
                        st.rerun()
                    except APIError as err:
                        st.error(f"Failed to create case: {err.message}")
        return

    # Case Selector in compact top bar
    if len(cases) > 1:
        case_options = {c["id"]: f"Case #{c['id']} — {c['case_code']}" for c in cases}
        selected_case_id = st.selectbox(
            "Active Support Case:",
            options=list(case_options.keys()),
            format_func=lambda x: case_options[x],
            key="selected_victim_case_id",
        )
        active_case = next((c for c in cases if c["id"] == selected_case_id), cases[0])
    else:
        active_case = cases[0]

    # Fetch active consent record
    consent = None
    try:
        consent = client.get_consent(token, active_case["id"])
    except APIError:
        pass

    # Route based on navigation selection
    if active_nav == "Overview":
        _render_victim_overview(client, token, user, active_case, consent)
    elif active_nav == "Well-being Check-In":
        _render_victim_checkin(client, token, user, active_case, consent)
    elif active_nav == "My Assessments":
        _render_victim_assessments(client, token, user, active_case)
    elif active_nav == "Support & Referrals":
        _render_victim_referrals(client, token, user, active_case)
    elif active_nav == "Consent & Privacy":
        _render_victim_consent(client, token, user, active_case, consent)
    elif active_nav == "Safe Contacts":
        _render_victim_contacts(client, token, user, active_case)
    else:
        _render_victim_overview(client, token, user, active_case, consent)


# ──────────────────────────────────────────────────────────
# 1. Victim Overview (Dashboard)
# ──────────────────────────────────────────────────────────

def _render_victim_overview(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
    active_case: dict[str, Any],
    consent: dict[str, Any] | None,
) -> None:
    """Render calm, un-cluttered healthcare overview screen."""

    username = user.get("username", "there")
    consent_status = consent.get("status", "not_granted") if consent else "not_granted"

    # Hero Banner with Primary CTA
    st.markdown(
        f"""
        <div class="ms-hero-banner">
            <h2 class="ms-hero-title">Welcome back, {username}</h2>
            <p class="ms-hero-subtitle">
                Your confidential space for trauma-informed mental health monitoring, care coordination, and recovery support.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Key Status Metrics (3 Columns)
    col1, col2, col3 = st.columns(3)

    with col1:
        c_badge = render_badge(consent_status)
        st.markdown(
            f"""
            <div class="ms-stat-card">
                <div class="ms-stat-label">Privacy & Consent</div>
                <div style="margin: 8px 0;">{c_badge}</div>
                <div class="ms-stat-desc">Case #{active_case['id']} • {active_case['case_code']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        # Load latest check-in
        latest_checkin = None
        try:
            checkins = client.get_case_checkins(token, active_case["id"])
            if checkins:
                latest_checkin = checkins[0]
        except APIError:
            pass

        if latest_checkin:
            r_level = latest_checkin.get("risk_level", "routine")
            r_badge = render_badge(r_level)
            checkin_date = latest_checkin.get("submitted_at", "")[:10]
            desc = f"Recorded on {checkin_date}"
        else:
            r_badge = '<span class="ms-badge ms-badge-neutral">No Check-Ins</span>'
            desc = "Ready for your first check-in"

        st.markdown(
            f"""
            <div class="ms-stat-card">
                <div class="ms-stat-label">Recent Assessment</div>
                <div style="margin: 8px 0;">{r_badge}</div>
                <div class="ms-stat-desc">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        # Load referral counts
        ref_count = 0
        try:
            referrals = client.get_case_referrals(token, active_case["id"])
            ref_count = len(referrals)
        except APIError:
            pass

        st.markdown(
            f"""
            <div class="ms-stat-card">
                <div class="ms-stat-label">Care Network</div>
                <div class="ms-stat-value">{ref_count}</div>
                <div class="ms-stat-desc">Active support referrals</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Primary Next-Step Action Card
    with st.container(border=True):
        st.markdown(
            """
            <h3 style="color: #0f4c5c; margin: 0 0 6px 0; font-size: 1.15rem;">
                Today's Daily Well-Being Check-In
            </h3>
            <p style="color: #475569; font-size: 0.9rem; margin: 0 0 14px 0;">
                A brief 2-minute questionnaire helps your caseworkers understand your emotional recovery trend
                and step in with timely assistance when you need it most.
            </p>
            """,
            unsafe_allow_html=True,
        )

        c_act, _ = st.columns([1, 2])
        with c_act:
            if consent_status == "granted":
                if st.button("Complete Daily Check-In →", type="primary", use_container_width=True):
                    st.session_state.current_nav = "Well-being Check-In"
                    st.rerun()
            else:
                st.caption(f"⚠️ Monitoring is currently **{consent_status.upper()}**. Please update consent to check in.")
                if st.button("Review Consent Settings", type="secondary", use_container_width=True):
                    st.session_state.current_nav = "Consent & Privacy"
                    st.rerun()

    # Lower Split Cards
    c_hist, c_help = st.columns([1.2, 1], gap="medium")

    with c_hist:
        with st.container(border=True):
            st.markdown(
                "<h4 style='color: #0f4c5c; margin-top: 0;'>Recent Progress Summary</h4>",
                unsafe_allow_html=True,
            )
            if latest_checkin:
                st.markdown(f"**Latest Check-In ID:** `#{latest_checkin.get('id')}`")
                st.markdown(f"**Submission Date:** {latest_checkin.get('submitted_at', '')[:16]}")
                st.markdown(f"**Recorded Distress Indicator:** `{latest_checkin.get('risk_level', 'routine').capitalize()}`")
                st.caption("Detailed longitudinal progress is available in the **My Assessments** view.")
            else:
                st.markdown(
                    """
                    <div class="ms-empty-state">
                        <div class="ms-empty-icon">📝</div>
                        <p style="margin: 0; font-size: 0.9rem;">No check-in history yet.<br>Complete your first check-in to view your trend.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with c_help:
        with st.container(border=True):
            st.markdown(
                "<h4 style='color: #0f4c5c; margin-top: 0;'>Urgent & Emergency Care</h4>",
                unsafe_allow_html=True,
            )
            st.markdown(
                """
                If you feel unsafe or are in immediate physical or psychological distress:
                * **Tele-MANAS:** `14416` (Toll-Free, 24/7 National Mental Health)
                * **Emergency Response:** `112`
                * **Women Helpline:** `1091`
                """
            )
            st.caption("Help is free, confidential, and available around the clock.")


# ──────────────────────────────────────────────────────────
# 2. Well-Being Check-In Form
# ──────────────────────────────────────────────────────────

def _render_victim_checkin(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
    active_case: dict[str, Any],
    consent: dict[str, Any] | None,
) -> None:
    """Render calm, trauma-informed well-being assessment form."""

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="color: #0f4c5c; margin-bottom: 4px;">Well-Being Check-In</h2>
            <p style="color: #475569; font-size: 0.9rem; margin: 0;">
                Take a moment to reflect on how you are feeling. There are no right or wrong answers.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    consent_status = consent.get("status") if consent else "not_granted"

    # Strict Consent Verification
    if consent_status != "granted":
        st.warning(
            f"🔒 **Check-ins are currently suspended.** Consent status: **{consent_status.upper()}**.\n\n"
            "Under the Digital Personal Data Protection (DPDP) Act, your monitoring consent must be active "
            "before responses can be processed."
        )
        if st.button("Review & Resume Consent", type="primary"):
            st.session_state.current_nav = "Consent & Privacy"
            st.rerun()
        return

    # Check-in form container
    with st.container(border=True):
        st.markdown(
            "<h4 style='color: #0f4c5c; margin-top: 0;'>1. Day-to-Day Well-Being Indicators</h4>",
            unsafe_allow_html=True,
        )

        with st.form("victim_checkin_form", clear_on_submit=False):
            q1 = st.selectbox(
                "How has your sleep been over the past 24-48 hours?",
                options=["none", "mild", "moderate", "severe"],
                format_func=lambda x: {
                    "none": "Normal / Restful — No noticeable sleep disturbance",
                    "mild": "Mild difficulty falling or staying asleep",
                    "moderate": "Interrupted sleep, night waking, or distressing dreams",
                    "severe": "Severe insomnia, nightmares, or feeling exhausted",
                }[x],
            )

            q2 = st.selectbox(
                "How intense have feelings of anxiety, stress, or tension been?",
                options=["none", "mild", "moderate", "severe"],
                format_func=lambda x: {
                    "none": "Calm / Manageable",
                    "mild": "Occasional worry or tension",
                    "moderate": "Frequent nervous exhaustion or panicky sensations",
                    "severe": "Constant overwhelming anxiety or intense dread",
                }[x],
            )

            q3 = st.selectbox(
                "Do you feel supported and connected with safe people around you?",
                options=["none", "mild", "moderate", "severe"],
                format_func=lambda x: {
                    "none": "I feel supported and have someone to turn to",
                    "mild": "Mild loneliness, but I have access to support",
                    "moderate": "Frequently feeling alone or disconnected",
                    "severe": "Completely isolated, no safe support network",
                }[x],
            )

            q4 = st.selectbox(
                "How manageable have daily tasks and personal routines felt?",
                options=["none", "mild", "moderate", "severe"],
                format_func=lambda x: {
                    "none": "Managing well / Feeling in control",
                    "mild": "Slightly harder than usual, but keeping up",
                    "moderate": "Significant difficulty focusing or doing chores",
                    "severe": "Unable to manage daily tasks or self-care",
                }[x],
            )

            st.markdown("---")
            st.markdown(
                "<h4 style='color: #0f4c5c; margin-top: 0;'>2. Optional Personal Reflection</h4>",
                unsafe_allow_html=True,
            )
            st.caption("You may share any specific thoughts, emotions, or situations in your own words. Our NLP system identifies distress markers for early intervention.")

            q_text = st.text_area(
                "Reflection Notes",
                placeholder="Share any thoughts, feelings, or challenges you faced today...",
                height=90,
                label_visibility="collapsed",
            )

            st.markdown("---")
            st.markdown(
                "<h4 style='color: #0f4c5c; margin-top: 0;'>3. Immediate Support Flags</h4>",
                unsafe_allow_html=True,
            )

            c_safe, c_hum = st.columns(2)
            with c_safe:
                direct_safety = st.checkbox(
                    "⚠️ I am experiencing an immediate safety threat or crisis.",
                    value=False,
                )
            with c_hum:
                request_contact = st.checkbox(
                    "📞 I would like a caseworker to reach out to me.",
                    value=False,
                )

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button(
                "Submit Confidential Check-In",
                type="primary",
                use_container_width=True,
            )

        if submit_btn:
            answers = [
                {"question_id": "sleep_quality", "answer": q1},
                {"question_id": "anxiety_intensity", "answer": q2},
                {"question_id": "isolation_feeling", "answer": q3},
                {"question_id": "coping_difficulty", "answer": q4},
            ]
            if q_text.strip():
                answers.append({"question_id": "free_reflection", "answer": q_text.strip()})

            with st.spinner("Processing your check-in securely..."):
                try:
                    result = client.submit_checkin(
                        token=token,
                        case_id=active_case["id"],
                        answers=answers,
                        questionnaire_version="v1",
                        direct_safety_concern=direct_safety,
                        requested_human_contact=request_contact,
                    )

                    risk_level = result.get("risk_level", "routine")
                    st.success(f"Check-in recorded successfully (Reference #{result.get('id')}).")

                    # Present reassuring, unalarming result card
                    if risk_level == "urgent":
                        st.error(
                            "🚨 **Priority Support Alert Dispatched**\n\n"
                            "Your responses indicate elevated distress or safety concern. "
                            "An alert has been dispatched to your support caseworker for immediate follow-up. "
                            "If you need immediate help, please call **Tele-MANAS at 14416** or **112**."
                        )
                    elif risk_level == "follow_up":
                        st.warning(
                            "🟡 **Follow-Up Recommended**\n\n"
                            "Moderate distress was recorded. Your care team will review this check-in. "
                            "Please consider reaching out to your safe contacts or taking time for restorative rest."
                        )
                    else:
                        st.info(
                            "🟢 **Routine Indicators**\n\n"
                            "Your check-in reflects stable emotional indicators. Thank you for checking in today."
                        )

                    st.caption("ℹ️ Note: AI outputs are decision-support indicators for trained caseworkers, not an automated clinical diagnosis.")

                except APIError as exc:
                    st.error(f"Check-in submission failed: {exc.message}")


# ──────────────────────────────────────────────────────────
# 3. Assessment History
# ──────────────────────────────────────────────────────────

def _render_victim_assessments(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
    active_case: dict[str, Any],
) -> None:
    """Render longitudinal check-in assessment history."""

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="color: #0f4c5c; margin-bottom: 4px;">My Assessment History</h2>
            <p style="color: #475569; font-size: 0.9rem; margin: 0;">
                Longitudinal record of your submitted check-ins and risk indicator levels.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        checkins = client.get_case_checkins(token, active_case["id"])
    except APIError as e:
        st.error(f"Failed to load check-ins: {e.message}")
        return

    if not checkins:
        st.markdown(
            """
            <div class="ms-empty-state">
                <div class="ms-empty-icon">📊</div>
                <h4 style="color: #0f4c5c; margin-bottom: 4px;">No Assessments Recorded Yet</h4>
                <p style="margin: 0; font-size: 0.9rem;">Once you complete a check-in, your history will appear here.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.write(f"Showing **{len(checkins)}** check-in assessment(s):")

    for item in checkins:
        cid = item.get("id")
        date_str = item.get("submitted_at", "")[:16].replace("T", " ")
        risk = item.get("risk_level") or "routine"
        badge = render_badge(risk)

        with st.container(border=True):
            c_info, c_badge = st.columns([3, 1])
            with c_info:
                st.markdown(f"**Check-In #{cid}** • Submitted on {date_str}")
                st.caption(f"Status: `{item.get('status', 'submitted')}` | Questionnaire: `{item.get('questionnaire_version', 'v1')}`")
            with c_badge:
                st.markdown(f"<div style='text-align: right;'>{badge}</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
# 4. Support Referrals
# ──────────────────────────────────────────────────────────

def _render_victim_referrals(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
    active_case: dict[str, Any],
) -> None:
    """Render support services referrals view."""

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="color: #0f4c5c; margin-bottom: 4px;">Support & Referrals</h2>
            <p style="color: #475569; font-size: 0.9rem; margin: 0;">
                Connect with verified external support partners for medical, legal aid, counselling, or shelter needs.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Request New Referral Expander
    with st.expander("➕ Request a New Referral for Support Services"):
        with st.form("new_referral_form"):
            ref_type = st.selectbox(
                "Service Category",
                options=["medical", "psychological_counselling", "legal_aid", "shelter", "financial_aid"],
                format_func=lambda x: x.replace("_", " ").title(),
            )
            org = st.text_input("Requested Provider or Organization", placeholder="e.g. District Legal Services Authority (DLSA) / Civil Hospital")
            reason = st.text_area("Description of Needs", placeholder="Describe the assistance you require...", height=80)
            priority = st.selectbox("Priority Level", options=["routine", "urgent"])
            sub_ref = st.form_submit_button("Submit Referral Request", type="primary")

        if sub_ref:
            if not org.strip() or not reason.strip():
                st.error("Please provide both an organization and description of your needs.")
            else:
                try:
                    client.create_referral(
                        token=token,
                        case_id=active_case["id"],
                        referral_type=ref_type,
                        organization=org.strip(),
                        reason=reason.strip(),
                        priority=priority,
                    )
                    st.success("Referral request submitted successfully!")
                    st.rerun()
                except APIError as e:
                    st.error(f"Failed to submit referral: {e.message}")

    # List Active Referrals
    try:
        referrals = client.get_case_referrals(token, active_case["id"])
    except APIError as e:
        st.error(f"Failed to load referrals: {e.message}")
        return

    if not referrals:
        st.markdown(
            """
            <div class="ms-empty-state">
                <div class="ms-empty-icon">🤝</div>
                <h4 style="color: #0f4c5c; margin-bottom: 4px;">No Active Referrals</h4>
                <p style="margin: 0; font-size: 0.9rem;">You have not requested any external support services yet.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for ref in referrals:
        rid = ref.get("id")
        status_val = ref.get("status", "created")
        badge = render_badge(status_val)
        prio_badge = render_badge(ref.get("priority", "routine"), text=f"{ref.get('priority', '').upper()} PRIORITY")

        with st.container(border=True):
            r1, r2 = st.columns([3, 1])
            with r1:
                st.markdown(f"**{ref.get('referral_type', '').replace('_', ' ').title()}** — *{ref.get('organization')}*")
                st.caption(f"Needs: {ref.get('reason')}")
            with r2:
                st.markdown(f"<div style='text-align: right;'>{badge} {prio_badge}</div>", unsafe_allow_html=True)

            if status_val == "created":
                if st.button(f"Acknowledge Referral #{rid}", key=f"ack_ref_{rid}"):
                    try:
                        client.update_referral_status(token, rid, "acknowledged")
                        st.success("Referral acknowledged.")
                        st.rerun()
                    except APIError as err:
                        st.error(err.message)


# ──────────────────────────────────────────────────────────
# 5. Consent & Privacy
# ──────────────────────────────────────────────────────────

def _render_victim_consent(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
    active_case: dict[str, Any],
    consent: dict[str, Any] | None,
) -> None:
    """Render digital consent and patient privacy controls."""

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="color: #0f4c5c; margin-bottom: 4px;">Consent & Privacy Governance</h2>
            <p style="color: #475569; font-size: 0.9rem; margin: 0;">
                You maintain sovereign control over your data in accordance with India's DPDP Act.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    consent_status = consent.get("status") if consent else "not_granted"

    with st.container(border=True):
        st.markdown("<h4 style='color: #0f4c5c; margin-top: 0;'>Current Monitoring Consent</h4>", unsafe_allow_html=True)
        st.markdown(f"**Consent Status:** {render_badge(consent_status)}", unsafe_allow_html=True)
        if consent:
            st.caption(f"Scope: `{consent.get('scope', 'monitoring')}` • Channel: `{consent.get('channel', 'web')}` • Granted: {consent.get('granted_at', 'N/A')[:10]}")
        else:
            st.caption("No consent record is on file. Please grant consent to enable well-being monitoring.")

        st.markdown("---")
        st.markdown("#### Change Consent State")

        c1, c2, c3 = st.columns(3)
        with c1:
            if consent_status in ("not_granted", "withdrawn"):
                if st.button("Grant Consent", type="primary", use_container_width=True):
                    try:
                        client.create_consent(token, active_case["id"], status="granted")
                        st.success("Consent granted.")
                        st.rerun()
                    except APIError as e:
                        st.error(e.message)
            elif consent_status == "paused":
                if st.button("Resume Consent", type="primary", use_container_width=True):
                    try:
                        client.update_consent_status(token, active_case["id"], "granted")
                        st.success("Consent resumed.")
                        st.rerun()
                    except APIError as e:
                        st.error(e.message)
        with c2:
            if consent_status == "granted":
                if st.button("Pause Monitoring", use_container_width=True):
                    try:
                        client.update_consent_status(token, active_case["id"], "paused")
                        st.warning("Consent paused.")
                        st.rerun()
                    except APIError as e:
                        st.error(e.message)
        with c3:
            if consent_status in ("granted", "paused"):
                if st.button("Withdraw Consent", use_container_width=True):
                    try:
                        client.update_consent_status(token, active_case["id"], "withdrawn")
                        st.error("Consent withdrawn.")
                        st.rerun()
                    except APIError as e:
                        st.error(e.message)


# ──────────────────────────────────────────────────────────
# 6. Safe Contacts Network
# ──────────────────────────────────────────────────────────

def _render_victim_contacts(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
    active_case: dict[str, Any],
) -> None:
    """Render trusted safe contacts management."""

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="color: #0f4c5c; margin-bottom: 4px;">Safe Contacts Network</h2>
            <p style="color: #475569; font-size: 0.9rem; margin: 0;">
                Designate trusted friends or relatives who can be contacted neutrally in case of emergency.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Add Safe Contact Form
    with st.expander("➕ Add Trusted Safe Contact"):
        with st.form("add_safe_contact_form"):
            c_name = st.text_input("Contact Name", placeholder="e.g. Suman Devi")
            c_rel = st.text_input("Relationship", placeholder="e.g. Sister, Trusted Friend, Community Elder")
            c_phone = st.text_input("Phone Number", placeholder="e.g. +91 9876543210")
            c_channel = st.selectbox("Preferred Channel", options=["call", "sms", "whatsapp"])
            c_time = st.text_input("Safe Contact Window", placeholder="e.g. Morning 10:00 AM - 12:00 PM")
            c_neutral = st.checkbox("Send Neutral Messages (Protects privacy by avoiding crisis keywords)", value=True)
            c_fallback = st.checkbox("Designate as Emergency Fallback Contact", value=False)
            sub_contact = st.form_submit_button("Save Contact", type="primary")

        if sub_contact:
            if not c_name.strip() or not c_rel.strip() or not c_phone.strip():
                st.error("Name, Relationship, and Phone Number are required.")
            else:
                try:
                    client.create_safe_contact(
                        token=token,
                        case_id=active_case["id"],
                        contact_name=c_name.strip(),
                        relationship=c_rel.strip(),
                        phone=c_phone.strip(),
                        preferred_channel=c_channel,
                        safe_time=c_time.strip() if c_time.strip() else None,
                        neutral_notification=c_neutral,
                        fallback_contact=c_fallback,
                    )
                    st.success("Safe contact saved.")
                    st.rerun()
                except APIError as e:
                    st.error(f"Failed to save contact: {e.message}")

    # List Contacts
    try:
        contacts = client.get_safe_contacts(token, active_case["id"])
    except APIError as e:
        st.error(f"Failed to load safe contacts: {e.message}")
        return

    active_contacts = [c for c in contacts if c.get("is_active", True)]
    if not active_contacts:
        st.markdown(
            """
            <div class="ms-empty-state">
                <div class="ms-empty-icon">🛡️</div>
                <h4 style="color: #0f4c5c; margin-bottom: 4px;">No Safe Contacts Configured</h4>
                <p style="margin: 0; font-size: 0.9rem;">Add a trusted contact who can be notified in an emergency.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for sc in active_contacts:
        cid = sc.get("id")
        with st.container(border=True):
            s1, s2 = st.columns([3, 1])
            with s1:
                st.markdown(f"**{sc.get('contact_name')}** ({sc.get('relationship')})")
                st.caption(f"Phone: `{sc.get('phone')}` • Channel: `{sc.get('preferred_channel')}` • Safe Time: {sc.get('safe_time') or 'Anytime'}")
            with s2:
                if st.button("Deactivate", key=f"deact_sc_{cid}"):
                    try:
                        client.deactivate_safe_contact(token, active_case["id"], cid)
                        st.success("Contact deactivated.")
                        st.rerun()
                    except APIError as e:
                        st.error(e.message)
