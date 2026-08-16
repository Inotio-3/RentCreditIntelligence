import streamlit as st
from config import DSR_THRESHOLD, DEMO_REPAYMENT_PERIOD, DEMO_INTEREST_RATE
from utils.ui import render_progress
from utils.helpers import money
from utils.state import reset_session_state
from logic.underwriting import calculate_assessment


def screen_decision():
    render_progress()

    results = calculate_assessment()

    advance_amount = float(
        st.session_state.get("saved_advance_amount")
        or st.session_state.get("advance_amount")
        or 0.0
    )
    monthly_rent = float(
        st.session_state.get("saved_monthly_rent")
        or st.session_state.get("monthly_rent")
        or 0.0
    )
    repayment_period = results["repayment_period"]
    is_salaried = results["is_salaried"]

    st.markdown(
        '<div class="section-title">Underwriting Decision & Verification</div>',
        unsafe_allow_html=True,
    )

    # Direct CSS fix for contrast: high-contrast text on warnings/badges
    st.markdown(
        """
        <style>
        /* Force dark high-contrast text on Streamlit warning boxes */
        div[data-baseweb="notification"] {
            color: #1e1e1e !important;
            font-weight: 500 !important;
        }
        div[data-baseweb="notification"] p {
            color: #1e1e1e !important;
        }
        .status-box.status-warn {
            background-color: #fff3cd !important;
            color: #212529 !important;
            border: 1px solid #ffeeba !important;
        }
        .result-value.warn {
            color: #d97706 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------
    # Top Result Cards
    # ------------------------------------------------------------
    c1, c2, c3 = st.columns(3)

    with c1:
        rent_status = "PASS" if results["rent_limit_pass"] else "FAIL"
        rent_kind = "pass" if results["rent_limit_pass"] else "fail"
        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-title">Rent-Advance Eligibility</div>
                <div class="result-value {rent_kind}">{rent_status}</div>
                <div class="small-note">
                    Requested: {money(advance_amount)}<br>
                    Cap Limit: {money(results["maximum_advance"])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        aff_kind = "pass" if results["affordability"] == "PASS" else "fail"
        dsr_display = (
            f"DSR: {results['dsr']:.1f}% | Limit: {DSR_THRESHOLD:.0f}%"
            if is_salaried and results["dsr"] is not None
            else "Cash flow & profit check"
        )
        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-title">Affordability</div>
                <div class="result-value {aff_kind}">
                    {results["affordability"]}
                </div>
                <div class="small-note">
                    {dsr_display}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        risk_kind = (
            "pass"
            if results["repayment_risk"] == "LOW"
            else "warn"
            if results["repayment_risk"] == "MEDIUM"
            else "fail"
        )
        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-title">Repayment Risk</div>
                <div class="result-value {risk_kind}">
                    {results["repayment_risk"]}
                </div>
                <div class="small-note">
                    Risk Score: {results.get('risk_score', 0.0):.1f} pts
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # Offer + Underwriting Analysis
    # ------------------------------------------------------------
    left, right = st.columns([1, 1], gap="large")

    with left:
        with st.container(border=True):
            st.markdown(
                '<div class="section-title">Conditional Offer & Breakdown</div>',
                unsafe_allow_html=True,
            )

            if results["conditional_offer"]:
                st.markdown(
                    f"""
                    <div class="green-card">
                        <div class="metric-label">POC Conditional Offer</div>
                        <div class="metric-value">{money(advance_amount)}</div>
                        <div class="small-note">
                            Proposed repayment: {money(results["monthly_repayment"])}
                            × {repayment_period} month(s)
                        </div>
                    </div>
                    <div class="status-box status-pass">
                        ✓ <strong>Conditional Offer Approved</strong><br>
                        Preliminary assessment meets all rent-advance, affordability, and risk criteria.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div class="status-box status-fail">
                        ✕ <strong>No Conditional Offer Granted</strong><br>
                        One or more primary credit or affordability constraints were not satisfied.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            st.markdown("##### **Underwriting Rationales & Breakdown**")

            # --- CALLOUT 1: Rent Advance Limit ---
            remaining_rent_buffer = (
                (results["maximum_advance"] - advance_amount) / monthly_rent
                if monthly_rent > 0
                else 0
            )
            if results["rent_limit_pass"]:
                st.success(
                    f"**Rent Advance Eligibility: PASS**\n\n"
                    f"• **Requested Advance:** {money(advance_amount)}\n"
                    f"• **Permitted Cap:** {money(results['maximum_advance'])} ({results['allowed_months']} months rent cap)\n"
                    f"• **Remaining Rent Buffer:** {remaining_rent_buffer:.1f} month(s) of rent under policy cap.\n\n"
                    f"✓ *Requested loan size is within policy boundaries for this tenancy duration.*"
                )
            else:
                st.error(
                    f"**Rent Advance Eligibility: FAIL**\n\n"
                    f"• **Requested Advance:** {money(advance_amount)}\n"
                    f"• **Permitted Cap:** {money(results['maximum_advance'])} ({results['allowed_months']} months rent cap)\n\n"
                    f"💡 *Underwriter Option: Cap requested advance at {money(results['maximum_advance'])}.*"
                )

            # --- CALLOUT 2: Affordability ---
            if is_salaried:
                salary_val = results["salary"]
                existing_debt_val = results["existing_debt"]
                monthly_installment = results["monthly_repayment"]

                if results["affordability"] == "PASS":
                    dsr_headroom = DSR_THRESHOLD - results["dsr"]
                    st.success(
                        f"**Affordability (Salaried): PASS**\n\n"
                        f"• **Net Monthly Salary:** {money(salary_val)}\n"
                        f"• **Total Debt Commitment:** {money(results['total_monthly_debt'])}/mo "
                        f"(Existing Debt: {money(existing_debt_val)} + New Installment: {money(monthly_installment)})\n"
                        f"• **Debt Service Ratio (DSR):** **{results['dsr']:.1f}%** (Policy Threshold: {DSR_THRESHOLD:.0f}%)\n"
                        f"• **Safety Margin:** {dsr_headroom:.1f}% under maximum DSR limit.\n\n"
                        f"✓ *Applicant demonstrates sufficient disposable income to cover monthly debt repayments.*"
                    )
                else:
                    st.error(
                        f"**Affordability (Salaried): FAIL**\n\n"
                        f"• **Net Monthly Salary:** {money(salary_val)}\n"
                        f"• **Total Debt Commitment:** {money(results['total_monthly_debt'])}/mo "
                        f"(Existing Debt: {money(existing_debt_val)} + New Installment: {money(monthly_installment)})\n"
                        f"• **Debt Service Ratio (DSR):** **{results['dsr']:.1f}%** (Policy Threshold: {DSR_THRESHOLD:.0f}%)\n\n"
                        f"💡 *Underwriter Options: Extend repayment term beyond {repayment_period} months to lower monthly repayments, "
                        f"or require partial debt payoff.*"
                    )
            else:
                if results["affordability"] == "PASS":
                    st.success(
                        f"**Affordability (Business): PASS**\n\n"
                        f"• **Proposed Monthly Repayment:** {money(results['monthly_repayment'])}/mo\n"
                        f"• **Business Cash Flow & Profit:** Operational liquidity and net profit cover the installment.\n\n"
                        f"✓ *Business generates sufficient net cash flow buffer for unencumbered repayment.*"
                    )
                else:
                    st.error(
                        f"**Affordability (Business): FAIL**\n\n"
                        f"• **Proposed Monthly Repayment:** {money(results['monthly_repayment'])}/mo\n"
                        f"• **Assessment:** Business net monthly cash flow or net profit is zero/negative or insufficient to cover repayments.\n\n"
                        f"💡 *Underwriter Options: Require a salaried guarantor or lower requested advance amount.*"
                    )

            # --- CALLOUT 3: Repayment Risk ---
            reasons_list = "\n• ".join(results["risk_reasons"])
            risk_score_val = results.get("risk_score", 0.0)

            if results["repayment_risk"] == "LOW":
                st.success(
                    f"**Repayment Risk: LOW (Score: {risk_score_val:.1f} pts)**\n\n"
                    f"• {reasons_list}\n\n"
                    f"✓ *{results['risk_rationale']}*"
                )
            elif results["repayment_risk"] == "MEDIUM":
                st.info(
                    f"**Repayment Risk: MEDIUM (Score: {risk_score_val:.1f} pts)**\n\n"
                    f"• {reasons_list}\n\n"
                    f"ℹ️ *{results['risk_rationale']}*",
                    icon="ℹ️",
                )
            else:
                st.warning(
                    f"**Repayment Risk: HIGH (Score: {risk_score_val:.1f} pts)**\n\n"
                    f"• {reasons_list}\n\n"
                    f"⚠️ *{results['risk_rationale']}*",
                    icon="⚠️",
                )

            if results["thin_credit"]:
                st.caption(
                    "ℹ️ **Thin Formal Credit History:** Applicant lacks extensive credit bureau records. "
                    "Assessed via job stability, employer tiering, or business cash flow."
                )

    with right:
        with st.container(border=True):
            st.markdown(
                '<div class="section-title">Verification Required</div>',
                unsafe_allow_html=True,
            )

            if is_salaried:
                verification_items = [
                    ("Payslip / salary evidence", st.session_state.get("payslip")),
                    ("Proof of employment", st.session_state.get("employment_proof")),
                    ("Existing debt information", None),
                    ("Rental / tenancy evidence", st.session_state.get("rental_proof")),
                    ("Credit information", None),
                ]
            else:
                verification_items = [
                    ("Business financial evidence", st.session_state.get("business_proof")),
                    ("Existing debt information", None),
                    ("Rental / tenancy evidence", st.session_state.get("rental_proof")),
                    ("Credit information", None),
                    (
                        "Guarantor evidence",
                        st.session_state.get("guarantor_proof")
                        if st.session_state.get("guarantor_available") == "Yes"
                        else None,
                    ),
                ]

            for label, uploaded in verification_items:
                status = (
                    "Uploaded — Verification pending"
                    if uploaded
                    else "Verification required"
                )
                status_class = "pass" if uploaded else "warn"

                st.markdown(
                    f"""
                    <div class="verify-row">
                        <span>• {label}</span>
                        <span class="verify-pending {status_class}">
                            {status}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                """
                <div class="status-box status-warn">
                    ⚠ Applicant-entered information must be validated before
                    final approval. This POC does not perform document,
                    employer, bank, or credit-bureau verification.
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # Rules & Assumptions
    # ------------------------------------------------------------
    with st.expander("Rules & POC assumptions"):
        st.markdown(
            f"""
            **Rental/legal rule used in this POC**
            - Tenancy > 6 months → maximum advance calculated at 6 months' rent.
            - Tenancy ≤ 6 months → maximum advance calculated at 2 months' rent.

            **Lender-provided assessment factors represented**
            - Salaried: salary, DSR, employment type, years at job, credit history.
            - Business: cash flow, profit, credit character, guarantor.

            **POC assumptions — lender validation required**
            - DSR threshold: **{DSR_THRESHOLD:.0f}%**
            - Default repayment period: **{DEMO_REPAYMENT_PERIOD} months**
            - Interest/fees: **{DEMO_INTEREST_RATE:.1f}%** for demonstration.
            - Risk model: weighted scoring model with probation & graduate consideration.
            """
        )

    if st.button("Start New Assessment", type="primary"):
        reset_session_state()
        st.rerun()










# import streamlit as st
# from config import DSR_THRESHOLD, DEMO_REPAYMENT_PERIOD, DEMO_INTEREST_RATE
# from utils.ui import render_progress
# from utils.helpers import money
# from utils.state import reset_session_state
# from logic.underwriting import calculate_assessment


# def screen_decision():
#     render_progress()

#     results = calculate_assessment()

#     advance_amount = float(
#         st.session_state.get("saved_advance_amount")
#         or st.session_state.get("advance_amount")
#         or 0.0
#     )
#     monthly_rent = float(
#         st.session_state.get("saved_monthly_rent")
#         or st.session_state.get("monthly_rent")
#         or 0.0
#     )
#     repayment_period = results["repayment_period"]
#     is_salaried = results["is_salaried"]

#     st.markdown(
#         '<div class="section-title">Underwriting Decision & Verification</div>',
#         unsafe_allow_html=True,
#     )

#     st.markdown(
#         """
#         <style>
#         .status-box.status-warn {
#             background-color: #fff3cd !important;
#             color: #856404 !important;
#             border: 1px solid #ffeeba !important;
#         }
#         .status-box.status-warn strong {
#             color: #533f03 !important;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )

#     # ------------------------------------------------------------
#     # Top Result Cards
#     # ------------------------------------------------------------
#     c1, c2, c3 = st.columns(3)

#     with c1:
#         rent_status = "PASS" if results["rent_limit_pass"] else "FAIL"
#         rent_kind = "pass" if results["rent_limit_pass"] else "fail"
#         st.markdown(
#             f"""
#             <div class="result-card">
#                 <div class="result-title">Rent-Advance Eligibility</div>
#                 <div class="result-value {rent_kind}">{rent_status}</div>
#                 <div class="small-note">
#                     Requested: {money(advance_amount)}<br>
#                     Cap Limit: {money(results["maximum_advance"])}
#                 </div>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )

#     with c2:
#         aff_kind = "pass" if results["affordability"] == "PASS" else "fail"
#         st.markdown(
#             f"""
#             <div class="result-card">
#                 <div class="result-title">Affordability</div>
#                 <div class="result-value {aff_kind}">
#                     {results["affordability"]}
#                 </div>
#                 <div class="small-note">
#                     """
#             + (
#                 f"DSR: {results['dsr']:.1f}% | Limit: {DSR_THRESHOLD:.0f}%"
#                 if is_salaried and results["dsr"] is not None
#                 else "Cash flow & profit check"
#             )
#             + """
#                 </div>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )

#     with c3:
#         risk_kind = (
#             "pass"
#             if results["repayment_risk"] == "LOW"
#             else "warn"
#             if results["repayment_risk"] == "MEDIUM"
#             else "fail"
#         )
#         st.markdown(
#             f"""
#             <div class="result-card">
#                 <div class="result-title">Repayment Risk</div>
#                 <div class="result-value {risk_kind}">
#                     {results["repayment_risk"]}
#                 </div>
#                 <div class="small-note">
#                     Risk Score: {results.get('risk_score', 0.0):.1f} pts
#                 </div>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )

#     st.markdown("<br>", unsafe_allow_html=True)

#     # ------------------------------------------------------------
#     # Offer + Underwriting Analysis
#     # ------------------------------------------------------------
#     left, right = st.columns([1, 1], gap="large")

#     with left:
#         with st.container(border=True):
#             st.markdown(
#                 '<div class="section-title">Conditional Offer & Breakdown</div>',
#                 unsafe_allow_html=True,
#             )

#             if results["conditional_offer"]:
#                 st.markdown(
#                     f"""
#                     <div class="green-card">
#                         <div class="metric-label">POC Conditional Offer</div>
#                         <div class="metric-value">{money(advance_amount)}</div>
#                         <div class="small-note">
#                             Proposed repayment: {money(results["monthly_repayment"])}
#                             × {repayment_period} month(s)
#                         </div>
#                     </div>
#                     <div class="status-box status-pass">
#                         ✓ <strong>Conditional Offer Approved</strong><br>
#                         Preliminary assessment meets all rent-advance, affordability, and risk criteria.
#                     </div>
#                     """,
#                     unsafe_allow_html=True,
#                 )
#             else:
#                 st.markdown(
#                     """
#                     <div class="status-box status-fail">
#                         ✕ <strong>No Conditional Offer Granted</strong><br>
#                         One or more primary credit or affordability constraints were not satisfied.
#                     </div>
#                     """,
#                     unsafe_allow_html=True,
#                 )

#             st.markdown("---")
#             st.markdown("##### **Underwriting Rationales & Breakdown**")

#             # --- CALLOUT 1: Rent Advance Limit ---
#             remaining_rent_buffer = (
#                 (results["maximum_advance"] - advance_amount) / monthly_rent
#                 if monthly_rent > 0
#                 else 0
#             )
#             if results["rent_limit_pass"]:
#                 st.success(
#                     f"**Rent Advance Eligibility: PASS**\n\n"
#                     f"• **Requested Advance:** {money(advance_amount)}\n"
#                     f"• **Permitted Cap:** {money(results['maximum_advance'])} ({results['allowed_months']} months rent cap)\n"
#                     f"• **Remaining Rent Buffer:** {remaining_rent_buffer:.1f} month(s) of rent under policy cap.\n\n"
#                     f"✓ *Requested loan size is within policy boundaries for this tenancy duration.*"
#                 )
#             else:
#                 st.error(
#                     f"**Rent Advance Eligibility: FAIL**\n\n"
#                     f"• **Requested Advance:** {money(advance_amount)}\n"
#                     f"• **Permitted Cap:** {money(results['maximum_advance'])} ({results['allowed_months']} months rent cap)\n\n"
#                     f"💡 *Underwriter Option: Cap requested advance at {money(results['maximum_advance'])}.*"
#                 )

#             # --- CALLOUT 2: Affordability ---
#             if is_salaried:
#                 salary_val = results["salary"] or 0.0
#                 existing_debt_val = results["existing_debt"]
#                 monthly_installment = results["monthly_repayment"]

#                 if results["affordability"] == "PASS" and results["dsr"] is not None:
#                     dsr_headroom = DSR_THRESHOLD - results["dsr"]
#                     st.success(
#                         f"**Affordability (Salaried): PASS**\n\n"
#                         f"• **Net Monthly Salary:** {money(salary_val)}\n"
#                         f"• **Total Debt Commitment:** {money(results['total_monthly_debt'])}/mo "
#                         f"(Existing Debt: {money(existing_debt_val)} + New Installment: {money(monthly_installment)})\n"
#                         f"• **Debt Service Ratio (DSR):** **{results['dsr']:.1f}%** (Policy Threshold: {DSR_THRESHOLD:.0f}%)\n"
#                         f"• **Safety Margin:** {dsr_headroom:.1f}% under maximum DSR limit.\n\n"
#                         f"✓ *Applicant demonstrates sufficient disposable income to cover monthly debt repayments.*"
#                     )
#                 else:
#                     dsr_val = results["dsr"] if results["dsr"] is not None else 0.0
#                     st.error(
#                         f"**Affordability (Salaried): FAIL**\n\n"
#                         f"• **Net Monthly Salary:** {money(salary_val)}\n"
#                         f"• **Total Debt Commitment:** {money(results['total_monthly_debt'])}/mo "
#                         f"(Existing Debt: {money(existing_debt_val)} + New Installment: {money(monthly_installment)})\n"
#                         f"• **Debt Service Ratio (DSR):** **{dsr_val:.1f}%** (Policy Threshold: {DSR_THRESHOLD:.0f}%)\n\n"
#                         f"💡 *Underwriter Options: Extend repayment term beyond {repayment_period} months to lower monthly repayments, "
#                         f"or require partial debt payoff.*"
#                     )
#             else:
#                 if results["affordability"] == "PASS":
#                     st.success(
#                         f"**Affordability (Business): PASS**\n\n"
#                         f"• **Proposed Monthly Repayment:** {money(results['monthly_repayment'])}/mo\n"
#                         f"• **Business Cash Flow & Profit:** Operational liquidity and net profit cover the installment.\n\n"
#                         f"✓ *Business generates sufficient net cash flow buffer for unencumbered repayment.*"
#                     )
#                 else:
#                     st.error(
#                         f"**Affordability (Business): FAIL**\n\n"
#                         f"• **Proposed Monthly Repayment:** {money(results['monthly_repayment'])}/mo\n"
#                         f"• **Assessment:** Business net monthly cash flow or net profit is zero/negative or insufficient to cover repayments.\n\n"
#                         f"💡 *Underwriter Options: Require a salaried guarantor or lower requested advance amount.*"
#                     )

#             # --- CALLOUT 3: Repayment Risk ---
#             reasons_list = "\n• ".join(results["risk_reasons"])
#             risk_score_val = results.get("risk_score", 0.0)

#             if results["repayment_risk"] == "LOW":
#                 st.success(
#                     f"**Repayment Risk: LOW (Score: {risk_score_val:.1f} pts)**\n\n"
#                     f"• {reasons_list}\n\n"
#                     f"✓ *{results['risk_rationale']}*"
#                 )
#             elif results["repayment_risk"] == "MEDIUM":
#                 st.info(
#                     f"**Repayment Risk: MEDIUM (Score: {risk_score_val:.1f} pts)**\n\n"
#                     f"• {reasons_list}\n\n"
#                     f"ℹ️ *{results['risk_rationale']}*",
#                     icon="ℹ️",
#                 )
#             else:
#                 st.warning(
#                     f"**Repayment Risk: HIGH (Score: {risk_score_val:.1f} pts)**\n\n"
#                     f"• {reasons_list}\n\n"
#                     f"⚠️ *{results['risk_rationale']}*",
#                     icon="⚠️",
#                 )

#             if results["thin_credit"]:
#                 st.caption(
#                     "ℹ️ **Thin Formal Credit History:** Applicant lacks extensive credit bureau records. "
#                     "Assessed via job stability, employer tiering, or business cash flow."
#                 )

#     with right:
#         with st.container(border=True):
#             st.markdown(
#                 '<div class="section-title">Verification Required</div>',
#                 unsafe_allow_html=True,
#             )

#             if is_salaried:
#                 verification_items = [
#                     ("Payslip / salary evidence", st.session_state.get("payslip")),
#                     ("Proof of employment", st.session_state.get("employment_proof")),
#                     ("Existing debt information", None),
#                     ("Rental / tenancy evidence", st.session_state.get("rental_proof")),
#                     ("Credit information", None),
#                 ]
#             else:
#                 verification_items = [
#                     ("Business financial evidence", st.session_state.get("business_proof")),
#                     ("Existing debt information", None),
#                     ("Rental / tenancy evidence", st.session_state.get("rental_proof")),
#                     ("Credit information", None),
#                     (
#                         "Guarantor evidence",
#                         st.session_state.get("guarantor_proof")
#                         if st.session_state.get("guarantor_available") == "Yes"
#                         else None,
#                     ),
#                 ]

#             for label, uploaded in verification_items:
#                 status = (
#                     "Uploaded — Verification pending"
#                     if uploaded
#                     else "Verification required"
#                 )
#                 status_class = "pass" if uploaded else "warn"

#                 st.markdown(
#                     f"""
#                     <div class="verify-row">
#                         <span>• {label}</span>
#                         <span class="verify-pending {status_class}">
#                             {status}
#                         </span>
#                     </div>
#                     """,
#                     unsafe_allow_html=True,
#                 )

#             st.markdown(
#                 """
#                 <div class="status-box status-warn">
#                     ⚠ Applicant-entered information must be validated before
#                     final approval. This POC does not perform document,
#                     employer, bank, or credit-bureau verification.
#                 </div>
#                 """,
#                 unsafe_allow_html=True,
#             )

#     st.markdown("<br>", unsafe_allow_html=True)

#     # ------------------------------------------------------------
#     # Rules & Assumptions
#     # ------------------------------------------------------------
#     with st.expander("Rules & POC assumptions"):
#         st.markdown(
#             f"""
#             **Rental/legal rule used in this POC**
#             - Tenancy > 6 months → maximum advance calculated at 6 months' rent.
#             - Tenancy ≤ 6 months → maximum advance calculated at 2 months' rent.

#             **Lender-provided assessment factors represented**
#             - Salaried: salary, DSR, employment type, years at job, credit history.
#             - Business: cash flow, profit, credit character, guarantor.

#             **POC assumptions — lender validation required**
#             - DSR threshold: **{DSR_THRESHOLD:.0f}%**
#             - Default repayment period: **{DEMO_REPAYMENT_PERIOD} months**
#             - Interest/fees: **{DEMO_INTEREST_RATE:.1f}%** for demonstration.
#             - Risk model: weighted scoring model with probation & graduate consideration.
#             """
#         )

#     if st.button("Start New Assessment", type="primary"):
#         reset_session_state()
#         st.rerun()









# # import streamlit as st
# # from config import DSR_THRESHOLD, DEMO_REPAYMENT_PERIOD, DEMO_INTEREST_RATE
# # from utils.ui import render_progress
# # from utils.helpers import money
# # from utils.state import reset_session_state
# # from logic.underwriting import calculate_assessment


# # def screen_decision():
# #     render_progress()

# #     # Get dynamic, safe assessment results
# #     results = calculate_assessment()

# #     # Retrieve input values safely
# #     advance_amount = float(
# #         st.session_state.get("saved_advance_amount")
# #         or st.session_state.get("advance_amount")
# #         or 0.0
# #     )
# #     repayment_period = max(
# #         int(st.session_state.get("repayment_period") or 1), 1
# #     )
# #     applicant_type = str(
# #         st.session_state.get("applicant_type") or "Salaried / Employed"
# #     )

# #     st.markdown(
# #         '<div class="section-title">Underwriting Decision & Verification</div>',
# #         unsafe_allow_html=True,
# #     )

# #     # ------------------------------------------------------------
# #     # Top Result Cards
# #     # ------------------------------------------------------------
# #     c1, c2, c3 = st.columns(3)

# #     with c1:
# #         rent_status = "PASS" if results["rent_limit_pass"] else "FAIL"
# #         rent_kind = "pass" if results["rent_limit_pass"] else "fail"
# #         st.markdown(
# #             f"""
# #             <div class="result-card">
# #                 <div class="result-title">Rent-Advance Eligibility</div>
# #                 <div class="result-value {rent_kind}">{rent_status}</div>
# #                 <div class="small-note">
# #                     Requested: {money(advance_amount)}<br>
# #                     Cap Limit: {money(results["maximum_advance"])}
# #                 </div>
# #             </div>
# #             """,
# #             unsafe_allow_html=True,
# #         )

# #     with c2:
# #         aff_kind = "pass" if results["affordability"] == "PASS" else "fail"
# #         st.markdown(
# #             f"""
# #             <div class="result-card">
# #                 <div class="result-title">Affordability</div>
# #                 <div class="result-value {aff_kind}">
# #                     {results["affordability"]}
# #                 </div>
# #                 <div class="small-note">
# #                     """
# #             + (
# #                 f"DSR: {results['dsr']:.1f}% | Limit: {DSR_THRESHOLD:.0f}%"
# #                 if results["dsr"] is not None
# #                 else "Business cash flow & profit assessment"
# #             )
# #             + """
# #                 </div>
# #             </div>
# #             """,
# #             unsafe_allow_html=True,
# #         )

# #     with c3:
# #         risk_kind = (
# #             "pass"
# #             if results["repayment_risk"] == "LOW"
# #             else "warn"
# #             if results["repayment_risk"] == "MEDIUM"
# #             else "fail"
# #         )
# #         st.markdown(
# #             f"""
# #             <div class="result-card">
# #                 <div class="result-title">Repayment Risk</div>
# #                 <div class="result-value {risk_kind}">
# #                     {results["repayment_risk"]}
# #                 </div>
# #                 <div class="small-note">
# #                     Risk Score: {results.get('risk_score', 0.0):.1f} pts
# #                 </div>
# #             </div>
# #             """,
# #             unsafe_allow_html=True,
# #         )

# #     st.markdown("<br>", unsafe_allow_html=True)

# #     # ------------------------------------------------------------
# #     # Offer + Comprehensive Dynamic Underwriting Analysis
# #     # ------------------------------------------------------------
# #     left, right = st.columns([1, 1], gap="large")

# #     with left:
# #         with st.container(border=True):
# #             st.markdown(
# #                 '<div class="section-title">Conditional Offer & Assessment Breakdown</div>',
# #                 unsafe_allow_html=True,
# #             )

# #             # --- CONDITIONAL OFFER SUMMARY CARD ---
# #             if results["conditional_offer"]:
# #                 st.markdown(
# #                     f"""
# #                     <div class="green-card">
# #                         <div class="metric-label">POC Conditional Offer</div>
# #                         <div class="metric-value">{money(advance_amount)}</div>
# #                         <div class="small-note">
# #                             Proposed repayment: {money(results["monthly_repayment"])}
# #                             × {repayment_period} month(s)
# #                         </div>
# #                     </div>
# #                     <div class="status-box status-pass">
# #                         ✓ <strong>Conditional Offer Approved</strong><br>
# #                         Preliminary assessment meets all rent-advance, affordability, and risk criteria.
# #                     </div>
# #                     """,
# #                     unsafe_allow_html=True,
# #                 )
# #             else:
# #                 st.markdown(
# #                     """
# #                     <div class="status-box status-fail">
# #                         ✕ <strong>No Conditional Offer Granted</strong><br>
# #                         One or more primary credit or affordability constraints were not satisfied.
# #                     </div>
# #                     """,
# #                     unsafe_allow_html=True,
# #                 )

# #             st.markdown("---")
# #             st.markdown("##### **Underwriting Rationales & Breakdown**")

# #             # --- CALLOUT 1: Rent Advance Limit (PASS vs FAIL) ---
# #             headroom = results["maximum_advance"] - advance_amount
# #             if results["rent_limit_pass"]:
# #                 st.success(
# #                     f"**Rent Advance Eligibility: PASS**\n\n"
# #                     f"• **Requested Advance:** {money(advance_amount)}\n"
# #                     f"• **Permitted Cap:** {money(results['maximum_advance'])} ({results['allowed_months']} months rent limit)\n"
# #                     f"• **Headroom Margin:** {money(headroom)} available under cap.\n\n"
# #                     f"✓ *The requested loan size is within policy boundaries for this tenancy duration.*"
# #                 )
# #             else:
# #                 excess = advance_amount - results["maximum_advance"]
# #                 st.error(
# #                     f"**Rent Advance Eligibility: FAIL**\n\n"
# #                     f"• **Requested Advance:** {money(advance_amount)}\n"
# #                     f"• **Permitted Cap:** {money(results['maximum_advance'])} ({results['allowed_months']} months rent limit)\n"
# #                     f"• **Exceeded Amount:** {money(excess)} over maximum cap.\n\n"
# #                     f"💡 *Underwriter Option: Cap requested advance at {money(results['maximum_advance'])}.*"
# #                 )

# #             # --- CALLOUT 2: Affordability & Debt Service (PASS vs FAIL) ---
# #             if results["affordability"] == "PASS":
# #                 if results["dsr"] is not None:
# #                     dsr_headroom = DSR_THRESHOLD - results["dsr"]
# #                     st.success(
# #                         f"**Affordability & Debt Service: PASS**\n\n"
# #                         f"• **Net Salary:** {money(results['salary'])}\n"
# #                         f"• **Total Debt Commitment:** {money(results['total_monthly_debt'])}/mo "
# #                         f"(Existing: {money(results['total_monthly_debt'] - results['monthly_repayment'])} + New: {money(results['monthly_repayment'])})\n"
# #                         f"• **Debt Service Ratio (DSR):** **{results['dsr']:.1f}%** (Policy limit: {DSR_THRESHOLD:.0f}%)\n"
# #                         f"• **Safety Margin:** {dsr_headroom:.1f}% under maximum DSR threshold.\n\n"
# #                         f"✓ *Applicant demonstrates adequate disposable income to service proposed monthly payments.*"
# #                     )
# #                 else:
# #                     st.success(
# #                         f"**Affordability & Cash Flow: PASS**\n\n"
# #                         f"• **Proposed Monthly Repayment:** {money(results['monthly_repayment'])}/mo\n"
# #                         f"• **Assessment:** Business operates with positive net cash flow and profit sufficient to cover installments.\n\n"
# #                         f"✓ *Sufficient cash flow buffer verified for unencumbered debt repayment.*"
# #                     )
# #             else:
# #                 if results["dsr"] is not None:
# #                     dsr_excess = results["dsr"] - DSR_THRESHOLD
# #                     st.error(
# #                         f"**Affordability & Debt Service: FAIL**\n\n"
# #                         f"• **Net Salary:** {money(results['salary'])}\n"
# #                         f"• **Total Debt Commitment:** {money(results['total_monthly_debt'])}/mo "
# #                         f"(Existing: {money(results['total_monthly_debt'] - results['monthly_repayment'])} + New: {money(results['monthly_repayment'])})\n"
# #                         f"• **Debt Service Ratio (DSR):** **{results['dsr']:.1f}%** (Policy limit: {DSR_THRESHOLD:.0f}%)\n"
# #                         f"• **Exceeded Threshold:** Over limit by {dsr_excess:.1f}%.\n\n"
# #                         f"💡 *Underwriter Options: Increase repayment term beyond {repayment_period} months to lower monthly repayment, "
# #                         f"or request partial payoff of existing obligations.*"
# #                     )
# #                 else:
# #                     st.error(
# #                         f"**Affordability & Cash Flow: FAIL**\n\n"
# #                         f"• **Proposed Monthly Repayment:** {money(results['monthly_repayment'])}/mo\n"
# #                         f"• **Assessment:** Business net monthly cash flow or net profit is zero/negative or insufficient to cover repayments.\n\n"
# #                         f"💡 *Underwriter Options: Require a salaried guarantor or reduce advance size.*"
# #                     )

# #             # --- CALLOUT 3: Repayment Risk & Score Breakdown ---
# #             reasons_list = "\n• ".join(results["risk_reasons"])
# #             risk_score_val = results.get("risk_score", 0.0)

# #             if results["repayment_risk"] == "LOW":
# #                 st.success(
# #                     f"**Repayment Risk: LOW (Score: {risk_score_val:.1f} pts)**\n\n"
# #                     f"• {reasons_list}\n\n"
# #                     f"✓ *{results['risk_rationale']}*"
# #                 )
# #             elif results["repayment_risk"] == "MEDIUM":
# #                 st.info(
# #                     f"**Repayment Risk: MEDIUM (Score: {risk_score_val:.1f} pts)**\n\n"
# #                     f"• {reasons_list}\n\n"
# #                     f"ℹ️ *{results['risk_rationale']}*",
# #                     icon="ℹ️",
# #                 )
# #             else:
# #                 st.warning(
# #                     f"**Repayment Risk: HIGH (Score: {risk_score_val:.1f} pts)**\n\n"
# #                     f"• {reasons_list}\n\n"
# #                     f"⚠️ *{results['risk_rationale']}*",
# #                     icon="⚠️",
# #                 )

# #             if results["thin_credit"]:
# #                 st.caption(
# #                     "ℹ️ **Thin Formal Credit History:** The applicant lacks extensive bureau history. "
# #                     "Underwriting relies on tenure stability, employer profile, or business cash flow indicators."
# #                 )

# #     with right:
# #         with st.container(border=True):
# #             st.markdown(
# #                 '<div class="section-title">Verification Required</div>',
# #                 unsafe_allow_html=True,
# #             )

# #             if applicant_type == "Salaried / Employed":
# #                 verification_items = [
# #                     ("Payslip / salary evidence", st.session_state.get("payslip")),
# #                     ("Proof of employment", st.session_state.get("employment_proof")),
# #                     ("Existing debt information", None),
# #                     ("Rental / tenancy evidence", st.session_state.get("rental_proof")),
# #                     ("Credit information", None),
# #                 ]
# #             else:
# #                 verification_items = [
# #                     ("Business financial evidence", st.session_state.get("business_proof")),
# #                     ("Existing debt information", None),
# #                     ("Rental / tenancy evidence", st.session_state.get("rental_proof")),
# #                     ("Credit information", None),
# #                     (
# #                         "Guarantor evidence",
# #                         st.session_state.get("guarantor_proof")
# #                         if st.session_state.get("guarantor_available") == "Yes"
# #                         else None,
# #                     ),
# #                 ]

# #             for label, uploaded in verification_items:
# #                 status = "Uploaded — Verification pending" if uploaded else "Verification required"
# #                 status_class = "pass" if uploaded else "warn"

# #                 st.markdown(
# #                     f"""
# #                     <div class="verify-row">
# #                         <span>• {label}</span>
# #                         <span class="verify-pending {status_class}">
# #                             {status}
# #                         </span>
# #                     </div>
# #                     """,
# #                     unsafe_allow_html=True,
# #                 )

# #             st.markdown(
# #                 """
# #                 <div class="status-box status-warn">
# #                     ⚠ Applicant-entered information must be validated before
# #                     final approval. This POC does not perform document,
# #                     employer, bank, or credit-bureau verification.
# #                 </div>
# #                 """,
# #                 unsafe_allow_html=True,
# #             )

# #     st.markdown("<br>", unsafe_allow_html=True)

# #     # ------------------------------------------------------------
# #     # Rules & Assumptions
# #     # ------------------------------------------------------------
# #     with st.expander("Rules & POC assumptions"):
# #         st.markdown(
# #             f"""
# #             **Rental/legal rule used in this POC**
# #             - Tenancy > 6 months → maximum advance calculated at 6 months' rent.
# #             - Tenancy ≤ 6 months → maximum advance calculated at 2 months' rent.

# #             **Lender-provided assessment factors represented**
# #             - Salaried: salary, DSR, employment type, years at job, credit history.
# #             - Business: cash flow, profit, credit character, guarantor.

# #             **POC assumptions — lender validation required**
# #             - DSR threshold: **{DSR_THRESHOLD:.0f}%**
# #             - Default repayment period: **{DEMO_REPAYMENT_PERIOD} months**
# #             - Interest/fees: **{DEMO_INTEREST_RATE:.1f}%** for demonstration.
# #             - Risk model: weighted scoring model with probation & graduate consideration.
# #             """
# #         )

# #     if st.button("Start New Assessment", type="primary"):
# #         reset_session_state()
# #         st.rerun()













# # import streamlit as st
# # from config import DSR_THRESHOLD, DEMO_REPAYMENT_PERIOD, DEMO_INTEREST_RATE, DEFAULTS
# # from utils.ui import render_progress
# # from utils.helpers import money, badge
# # from utils.state import reset_session_state
# # from logic.underwriting import calculate_assessment


# # def screen_decision():
# #     render_progress()

# #     results = calculate_assessment()

# #     st.markdown(
# #         '<div class="section-title">Underwriting Decision & Verification</div>',
# #         unsafe_allow_html=True,
# #     )

# #     # ------------------------------------------------------------
# #     # Top result cards
# #     # ------------------------------------------------------------
# #     c1, c2, c3 = st.columns(3)

# #     with c1:
# #         rent_status = "PASS" if results["rent_limit_pass"] else "FAIL"
# #         rent_kind = "pass" if results["rent_limit_pass"] else "fail"
# #         st.markdown(
# #             f"""
# #             <div class="result-card">
# #                 <div class="result-title">Rent-Advance Eligibility</div>
# #                 <div class="result-value {rent_kind}">{rent_status}</div>
# #                 <div class="small-note">
# #                     Requested: {money(st.session_state.advance_amount)}<br>
# #                     Applicable limit: {money(results["maximum_advance"])}
# #                 </div>
# #             </div>
# #             """,
# #             unsafe_allow_html=True,
# #         )

# #     with c2:
# #         aff_kind = "pass" if results["affordability"] == "PASS" else "fail"
# #         st.markdown(
# #             f"""
# #             <div class="result-card">
# #                 <div class="result-title">Affordability</div>
# #                 <div class="result-value {aff_kind}">
# #                     {results["affordability"]}
# #                 </div>
# #                 <div class="small-note">
# #                     """
# #             + (
# #                 f"DSR: {results['dsr']:.1f}%<br>Demo threshold: {DSR_THRESHOLD:.0f}%"
# #                 if results["dsr"] is not None
# #                 else "Business cash flow/profit assessment"
# #             )
# #             + """
# #                 </div>
# #             </div>
# #             """,
# #             unsafe_allow_html=True,
# #         )

# #     with c3:
# #         risk_kind = (
# #             "pass" if results["repayment_risk"] == "LOW"
# #             else "warn" if results["repayment_risk"] == "MEDIUM"
# #             else "fail"
# #         )
# #         st.markdown(
# #             f"""
# #             <div class="result-card">
# #                 <div class="result-title">Repayment Risk</div>
# #                 <div class="result-value {risk_kind}">
# #                     {results["repayment_risk"]}
# #                 </div>
# #                 <div class="small-note">
# #                     Illustrative POC risk result
# #                 </div>
# #             </div>
# #             """,
# #             unsafe_allow_html=True,
# #         )

# #     st.markdown("<br>", unsafe_allow_html=True)

# #     # ------------------------------------------------------------
# #     # Offer + verification
# #     # ------------------------------------------------------------
# #     left, right = st.columns([1, 1], gap="large")

# #     with left:
# #         with st.container(border=True):
# #             st.markdown('<div class="section-title">Conditional Offer</div>', unsafe_allow_html=True)

# #             if results["conditional_offer"]:
# #                 st.markdown(
# #                     f"""
# #                     <div class="green-card">
# #                         <div class="metric-label">POC Conditional Offer</div>
# #                         <div class="metric-value">{money(st.session_state.advance_amount)}</div>
# #                         <div class="small-note">
# #                             Proposed repayment: {money(results["monthly_repayment"])}
# #                             × {st.session_state.repayment_period} month(s)
# #                         </div>
# #                     </div>
# #                     """,
# #                     unsafe_allow_html=True,
# #                 )

# #                 st.markdown(
# #                     """
# #                     <div class="status-box status-pass">
# #                         ✓ <strong>Conditional Offer</strong><br>
# #                         Preliminary assessment supports an offer subject to
# #                         required verification and final lender approval.
# #                     </div>
# #                     """,
# #                     unsafe_allow_html=True,
# #                 )
# #             else:
# #                 st.markdown(
# #                     """
# #                     <div class="status-box status-fail">
# #                         ✕ <strong>No Conditional Offer at this stage</strong><br>
# #                         One or more configured POC conditions are not satisfied.
# #                     </div>
# #                     """,
# #                     unsafe_allow_html=True,
# #                 )

# #             if results["thin_credit"]:
# #                 st.markdown(
# #                     """
# #                     <div class="status-box status-warn">
# #                         ⚠ <strong>Limited formal credit history</strong><br>
# #                         The applicant was not automatically rejected because
# #                         of limited/no formal credit history. Verification of
# #                         the available indicators is still required.
# #                     </div>
# #                     """,
# #                     unsafe_allow_html=True,
# #                 )

# #             st.markdown(
# #                 """
# #                 <div class="rule-note">
# #                     This is a preliminary POC assessment, not a final credit
# #                     approval or binding lending offer.
# #                 </div>
# #                 """,
# #                 unsafe_allow_html=True,
# #             )

# #     with right:
# #         with st.container(border=True):
# #             st.markdown('<div class="section-title">Verification Required</div>', unsafe_allow_html=True)

# #             if st.session_state.applicant_type == "Salaried / Employed":
# #                 verification_items = [
# #                     ("Payslip / salary evidence", st.session_state.payslip),
# #                     ("Proof of employment", st.session_state.employment_proof),
# #                     ("Existing debt information", None),
# #                     ("Rental / tenancy evidence", st.session_state.rental_proof),
# #                     ("Credit information", None),
# #                 ]
# #             else:
# #                 verification_items = [
# #                     ("Business financial evidence", st.session_state.business_proof),
# #                     ("Existing debt information", None),
# #                     ("Rental / tenancy evidence", st.session_state.rental_proof),
# #                     ("Credit information", None),
# #                     (
# #                         "Guarantor evidence",
# #                         st.session_state.guarantor_proof
# #                         if st.session_state.guarantor_available == "Yes"
# #                         else None,
# #                     ),
# #                 ]

# #             for label, uploaded in verification_items:
# #                 status = "Uploaded — Verification pending" if uploaded else "Verification required"
# #                 status_class = "pass" if uploaded else "warn"

# #                 st.markdown(
# #                     f"""
# #                     <div class="verify-row">
# #                         <span>• {label}</span>
# #                         <span class="verify-pending {status_class}">
# #                             {status}
# #                         </span>
# #                     </div>
# #                     """,
# #                     unsafe_allow_html=True,
# #                 )

# #             st.markdown(
# #                 """
# #                 <div class="status-box status-warn">
# #                     ⚠ Applicant-entered information must be validated before
# #                     final approval. This POC does not perform document,
# #                     employer, bank, or credit-bureau verification.
# #                 </div>
# #                 """,
# #                 unsafe_allow_html=True,
# #             )

# #     st.markdown("<br>", unsafe_allow_html=True)

# #     # ------------------------------------------------------------
# #     # Rules & assumptions
# #     # ------------------------------------------------------------
# #     with st.expander("Rules & POC assumptions"):
# #         st.markdown(
# #             f"""
# #             **Rental/legal rule used in this POC**
# #             - Tenancy > 6 months → maximum advance calculated at 6 months' rent.
# #             - Tenancy ≤ 6 months → maximum advance calculated at 2 months' rent.

# #             **Lender-provided assessment factors represented**
# #             - Salaried: salary, DSR, employment type, years at job, credit history.
# #             - Business: cash flow, profit, credit character, guarantor.

# #             **POC assumptions — lender validation required**
# #             - DSR threshold: **{DSR_THRESHOLD:.0f}%**
# #             - Default repayment period: **{DEMO_REPAYMENT_PERIOD} months**
# #             - Interest/fees: **{DEMO_INTEREST_RATE:.1f}%** for demonstration.
# #             - Risk model: illustrative LOW/MEDIUM/HIGH scoring.
# #             - Business affordability: simplified cash-flow/profit rule.

# #             **Important:** The prototype demonstrates an underwriting workflow.
# #             It is not a production credit-scoring or approval system.
# #             """
# #         )

# #     if st.button("Start New Assessment", type="primary"):
# #         reset_session_state()
# #         st.rerun()
