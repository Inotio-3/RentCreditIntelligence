import streamlit as st
from utils.helpers import calculate_rent_advance_limit, money, parse_tenancy_months
from utils.ui import render_progress


def init_rent_state():
    """Ensure persistence keys exist in session state before rendering UI elements."""
    if "saved_monthly_rent" not in st.session_state:
        st.session_state.saved_monthly_rent = 0.0
    if "saved_advance_amount" not in st.session_state:
        st.session_state.saved_advance_amount = 0.0
    if "saved_tenancy_duration" not in st.session_state:
        st.session_state.saved_tenancy_duration = None
    if "saved_purpose" not in st.session_state:
        st.session_state.saved_purpose = None


def screen_rent():
    init_rent_state()
    render_progress()

    left, right = st.columns([1.65, 0.85], gap="large")

    with left:
        with st.container(border=True):
            st.markdown(
                '<div class="section-title">Applicant & Rent Details</div>',
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns(2)

            with c1:
                # Use dedicated input keys distinct from standard storage key names
                monthly_rent = st.number_input(
                    "Monthly Rent (GHS)",
                    min_value=0.0,
                    step=100.0,
                    value=float(
                        st.session_state.get("saved_monthly_rent")
                        or st.session_state.get("monthly_rent")
                        or 0.0
                    ),
                    placeholder="Enter monthly rent",
                    key="input_monthly_rent",
                )

                advance_amount = st.number_input(
                    "Rent Advance Requested (GHS)",
                    min_value=0.0,
                    step=100.0,
                    value=float(
                        st.session_state.get("saved_advance_amount")
                        or st.session_state.get("advance_amount")
                        or 0.0
                    ),
                    placeholder="Enter requested advance",
                    key="input_advance_amount",
                )

            with c2:
                durations = [
                    "1 month",
                    "2 months",
                    "3 months",
                    "6 months",
                    "12 months",
                    "24 months",
                ]

                current_duration = st.session_state.get(
                    "saved_tenancy_duration"
                ) or st.session_state.get("tenancy_duration")
                duration_index = (
                    durations.index(current_duration)
                    if current_duration in durations
                    else None
                )

                tenancy_duration = st.selectbox(
                    "Tenancy Duration",
                    durations,
                    index=duration_index,
                    placeholder="Select tenancy duration",
                    key="input_tenancy_duration",
                )

            purposes = [
                "New Tenancy Agreement",
                "Tenancy Renewal",
                "Other housing purpose",
            ]
            current_purpose = st.session_state.get(
                "saved_purpose"
            ) or st.session_state.get("purpose")
            purpose_index = (
                purposes.index(current_purpose)
                if current_purpose in purposes
                else None
            )

            selected_purpose = st.selectbox(
                "Purpose of Advance",
                purposes,
                index=purpose_index,
                placeholder="Select purpose",
                key="input_purpose",
            )

            st.markdown("<br>", unsafe_allow_html=True)
            b1, b2 = st.columns([1, 2])

            with b1:
                if st.button("← Back", use_container_width=True):
                    st.session_state.step = 0
                    st.rerun()

            valid = (
                (monthly_rent or 0) > 0
                and (advance_amount or 0) > 0
                and tenancy_duration is not None
                and selected_purpose is not None
            )

            with b2:
                if st.button(
                    "Continue to Financials",
                    type="primary",
                    use_container_width=True,
                    disabled=not valid,
                ):
                    # Save into tracking session keys
                    st.session_state["saved_monthly_rent"] = monthly_rent
                    st.session_state["saved_advance_amount"] = advance_amount
                    st.session_state["saved_tenancy_duration"] = tenancy_duration
                    st.session_state["saved_purpose"] = selected_purpose

                    # Store in main keys for cross-script logic
                    st.session_state["monthly_rent"] = monthly_rent
                    st.session_state["advance_amount"] = advance_amount
                    st.session_state["tenancy_duration"] = tenancy_duration
                    st.session_state["purpose"] = selected_purpose

                    st.session_state.rent_debug = {
                        "monthly_rent": monthly_rent,
                        "advance_amount": advance_amount,
                        "tenancy_duration": tenancy_duration,
                    }

                    st.session_state.step = 2
                    st.rerun()

            if not valid:
                st.caption(
                    "Complete all applicant and rent fields to continue."
                )

    with right:
        with st.container(border=True):
            st.markdown(
                '<div class="section-title">Calculation Engine & Rules</div>',
                unsafe_allow_html=True,
            )

            if (
                not monthly_rent
                or not advance_amount
                or not tenancy_duration
            ):
                st.markdown(
                    """
                    <div class="soft-card">
                        <div class="metric-label">Applicable Rent-Advance Limit</div>
                        <div class="metric-value">Awaiting input</div>
                        <div class="small-note">
                            Enter rent, requested advance and tenancy duration
                            to calculate the limit.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                months = parse_tenancy_months(tenancy_duration)
                allowed_months, max_advance = calculate_rent_advance_limit(
                    monthly_rent,
                    months,
                )
                rent_pass = advance_amount <= max_advance
                st.session_state.rent_limit_pass = rent_pass

                st.markdown(
                    f"""
                    <div class="green-card">
                        <div class="metric-label">Applicable Rent-Advance Limit</div>
                        <div class="metric-value">{money(max_advance)}</div>
                        <div class="small-note">
                            Formula: Monthly Rent ({money(monthly_rent)})
                            × {allowed_months} month(s)
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if rent_pass:
                    st.markdown(
                        f"""
                        <div class="status-box status-pass">
                            ✓ <strong>Within Rent-Advance Limit</strong><br>
                            Advance requested ({money(advance_amount)})
                            ≤ limit ({money(max_advance)})
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        """
                        <div class="status-box status-fail">
                            <strong>Above Rent-Advance Limit</strong><br>
                            Requested amount exceeds the calculated POC limit as determined by the Ghana Rent Act.<br>
                            Please deliberate with your Landlord for an acceptable rent advance or key in the applicable rent advance limit to proceed
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown(
                """
                <div class="rule-note">
                    <div class="section-title">NB: Rental/legal rule — not a lender risk threshold. Subject to lender review</div>
                </div>
                """,
                unsafe_allow_html=True,
            )