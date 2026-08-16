import streamlit as st
from config import DSR_THRESHOLD
from logic.underwriting import calculate_assessment
from utils.helpers import badge, money
from utils.ui import render_progress


def screen_underwriting():
    render_progress()

    # Apply inline CSS for high-contrast badge & warning styling
    st.markdown(
        """
        <style>
        .status-box.status-warn {
            background-color: #fff3cd !important;
            color: #212529 !important;
            border: 1px solid #ffeeba !important;
        }
        .badge.warn {
            background-color: #fef3c7 !important;
            color: #92400e !important;
            border: 1px solid #fde68a !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- 1. Fetch primary values safely with fallback chains ---
    monthly_rent = (
        st.session_state.get("saved_monthly_rent")
        if st.session_state.get("saved_monthly_rent") is not None
        else st.session_state.get("monthly_rent")
    )
    advance_amount = (
        st.session_state.get("saved_advance_amount")
        if st.session_state.get("saved_advance_amount") is not None
        else st.session_state.get("advance_amount")
    )
    tenancy_duration = st.session_state.get(
        "saved_tenancy_duration"
    ) or st.session_state.get("tenancy_duration")

    # --- 2. Validate presence of required initial inputs ---
    if tenancy_duration is None or monthly_rent is None or advance_amount is None:
        st.error(
            "Please complete the tenancy and rent information before continuing."
        )
        if st.button("← Go back to Rent Details"):
            st.session_state.step = 1
            st.rerun()
        st.stop()

    # --- 3. Execute underwriter calculations ---
    results = calculate_assessment()

    # Pull calculated or resolved state variables
    repayment_period = results.get("repayment_period", 12)
    existing_debt = results.get("existing_debt", 0.0)
    salary = results.get("salary", 0.0)

    applicant_type = (
        st.session_state.get("saved_applicant_type")
        or st.session_state.get("applicant_type")
        or "Salaried / Employed"
    )
    is_salaried = results.get("is_salaried", True)

    left, right = st.columns([1, 1], gap="large")

    with left:
        with st.container(border=True):
            dsr_label = (
                "Affordability Assessment (DSR)"
                if is_salaried
                else "Affordability Assessment (Business)"
            )

            st.markdown(
                f'<div class="section-title">{dsr_label}</div>',
                unsafe_allow_html=True,
            )

            if results["affordability"] == "PASS":
                st.markdown(
                    badge("AFFORDABILITY: PASS", "pass"), unsafe_allow_html=True
                )
            else:
                st.markdown(
                    badge("AFFORDABILITY: FAIL", "fail"), unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)

            if is_salaried:
                dsr_val = (
                    f"{results['dsr']:.1f}%"
                    if results.get("dsr") is not None
                    else "N/A"
                )

                st.markdown(
                    f"""
                    <div class="soft-card">
                        <div class="metric-label">DSR Calculation Chain</div>
                        <br>
                        <div style="font-size:11px;">
                            <strong>Net Monthly Salary</strong>
                            <span style="float:right;">
                                <strong>{money(salary)}</strong>
                            </span>
                        </div>
                        <hr style="border:none;border-top:1px solid #e6ebf1;">
                        <div style="font-size:11px;">
                            <strong>New Monthly Repayment</strong>
                            <span style="float:right;">
                                {money(advance_amount)} ÷ {repayment_period} mo = <strong>{money(results['monthly_repayment'])}/mo</strong>
                            </span>
                        </div>
                        <hr style="border:none;border-top:1px solid #e6ebf1;">
                        <div style="font-size:11px;">
                            <strong>Total Monthly Debt</strong>
                            <span style="float:right;">
                                {money(existing_debt)} + {money(results['monthly_repayment'])} = <strong>{money(results['total_monthly_debt'])}/mo</strong>
                            </span>
                        </div>
                        <hr style="border:none;border-top:1px solid #e6ebf1;">
                        <div style="font-size:12px;color:#006b57;">
                            <strong>Final Debt-to-Income (DSR)</strong>
                            <span style="float:right;">
                                {dsr_val}
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if results.get("dsr") is not None and salary > 0:
                    st.progress(
                        min(max(results["dsr"] / DSR_THRESHOLD, 0.0), 1.0)
                    )
                    st.caption(
                        f"{results['dsr']:.1f}% "
                        f"(Demo threshold: {DSR_THRESHOLD:.0f}%)"
                    )
                else:
                    st.warning("Valid salary (> 0) is required to calculate DSR.")

            else:
                cash_flow = (
                    st.session_state.get("saved_business_cash_flow")
                    or st.session_state.get("business_cash_flow")
                    or 0.0
                )
                profit = (
                    st.session_state.get("saved_business_profit")
                    or st.session_state.get("business_profit")
                    or 0.0
                )
                repayment = results["monthly_repayment"]

                st.markdown(
                    f"""
                    <div class="soft-card">
                        <div class="metric-label">Business Affordability Chain</div>
                        <br>
                        <div style="font-size:11px;">
                            <strong>Average Cash Flow</strong>
                            <span style="float:right;">{money(cash_flow)}</span>
                        </div>
                        <hr style="border:none;border-top:1px solid #e6ebf1;">
                        <div style="font-size:11px;">
                            <strong>Profit</strong>
                            <span style="float:right;">{money(profit)}</span>
                        </div>
                        <hr style="border:none;border-top:1px solid #e6ebf1;">
                        <div style="font-size:11px;">
                            <strong>Proposed Repayment</strong>
                            <span style="float:right;">{money(repayment)}/mo</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    '<div class="status-box status-info">'
                    "Simplified POC rule: positive profit + positive cash flow "
                    "and cash flow sufficient to cover proposed repayment."
                    "</div>",
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"""
                <div class="rule-note">
                    ⚠ Repayment period ({repayment_period} months)
                    is determined by lender/product policy.<br>
                    ⚠ DSR threshold ({DSR_THRESHOLD:.0f}%) is a demo assumption —
                    lender validation required.
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        with st.container(border=True):
            risk_class = (
                "pass"
                if results["repayment_risk"] == "LOW"
                else (
                    "warn" if results["repayment_risk"] == "MEDIUM" else "fail"
                )
            )

            st.markdown(
                f"""
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div class="section-title" style="margin:0;">
                        Repayment Risk & Qualitative Factors
                    </div>
                    <span class="badge {risk_class}">
                        REPAYMENT RISK: {results["repayment_risk"]}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)

            for reason in results.get("risk_reasons", []):
                st.markdown(
                    f"""
                    <div style="font-size:11px;margin-bottom:10px;">
                        <span style="color:#006b57;font-weight:700;">✓</span>
                        {reason}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if results.get("thin_credit"):
                st.markdown(
                    """
                    <div class="status-box status-warn">
                        ⚠ <strong>Thin formal credit history</strong><br>
                        Risk assessment uses the other available indicators.
                        Limited credit history should not automatically result
                        in rejection in this POC.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"""
                <div class="soft-card" style="margin-top:12px;">
                    <div style="font-size:10px;color:#68788c;font-weight:700;">
                        RISK RATIONALE
                    </div>
                    <div style="font-size:10px;color:#68788c;margin-top:5px;line-height:1.5;">
                        {results.get("risk_rationale", "")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="rule-note">
                    ⚠ Illustrative POC risk model — not a lender-approved
                    credit score. Replace the demo scoring logic with validated
                    lender rules.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            b1, b2 = st.columns([1, 2])
            with b1:
                if st.button("← Back", use_container_width=True):
                    st.session_state.step = 2
                    st.rerun()
            with b2:
                if st.button(
                    "Generate Decision", type="primary", use_container_width=True
                ):
                    st.session_state.step = 4
                    st.session_state.verification_run = True
                    st.rerun()










# import streamlit as st
# from config import DSR_THRESHOLD
# from logic.underwriting import calculate_assessment
# from utils.helpers import badge, money
# from utils.ui import render_progress


# def screen_underwriting():
#     render_progress()

#     # --- 1. Fetch values safely from saved state or fallback keys ---
#     monthly_rent = (
#         st.session_state.get("saved_monthly_rent")
#         if st.session_state.get("saved_monthly_rent") is not None
#         else st.session_state.get("monthly_rent")
#     )
#     advance_amount = (
#         st.session_state.get("saved_advance_amount")
#         if st.session_state.get("saved_advance_amount") is not None
#         else st.session_state.get("advance_amount")
#     )
#     tenancy_duration = st.session_state.get(
#         "saved_tenancy_duration"
#     ) or st.session_state.get("tenancy_duration")

#     # --- 2. Validate presence of data ---
#     if tenancy_duration is None or monthly_rent is None or advance_amount is None:
#         st.error(
#             "Please complete the tenancy and rent information before continuing."
#         )
#         if st.button("← Go back to Rent Details"):
#             st.session_state.step = 1
#             st.rerun()
#         st.stop()

#     # --- 3. Execute calculations ---
#     results = calculate_assessment()

#     # Fetch safe secondary values for UI rendering
#     repayment_period = st.session_state.get("repayment_period", 12)
#     existing_debt = st.session_state.get("existing_debt", 0.0)
#     applicant_type = st.session_state.get(
#         "applicant_type", "Salaried / Employed"
#     )

#     left, right = st.columns([1, 1], gap="large")

#     with left:
#         with st.container(border=True):
#             dsr_label = "Affordability Assessment (DSR)"
#             if applicant_type != "Salaried / Employed":
#                 dsr_label = "Affordability Assessment (Business)"

#             st.markdown(
#                 f'<div class="section-title">{dsr_label}</div>',
#                 unsafe_allow_html=True,
#             )

#             if results["affordability"] == "PASS":
#                 st.markdown(
#                     badge("AFFORDABILITY: PASS", "pass"), unsafe_allow_html=True
#                 )
#             else:
#                 st.markdown(
#                     badge("AFFORDABILITY: FAIL", "fail"), unsafe_allow_html=True
#                 )

#             st.markdown("<br>", unsafe_allow_html=True)

#             if applicant_type == "Salaried / Employed":
#                 dsr_val = (
#                     f"{results['dsr']:.1f}%"
#                     if results.get("dsr") is not None
#                     else "N/A"
#                 )

#                 st.markdown(
#                     f"""
#                     <div class="soft-card">
#                         <div class="metric-label">DSR Calculation Chain</div>
#                         <br>
#                         <div style="font-size:11px;">
#                             <strong>New Monthly Repayment</strong>
#                             <span style="float:right;">
#                                 {money(advance_amount)}
#                                 ÷ {repayment_period} months
#                                 = <strong>{money(results['monthly_repayment'])}/mo</strong>
#                             </span>
#                         </div>
#                         <hr style="border:none;border-top:1px solid #e6ebf1;">
#                         <div style="font-size:11px;">
#                             <strong>Total Monthly Debt</strong>
#                             <span style="float:right;">
#                                 {money(existing_debt)}
#                                 + {money(results['monthly_repayment'])}
#                                 = <strong>{money(results['total_monthly_debt'])}/mo</strong>
#                             </span>
#                         </div>
#                         <hr style="border:none;border-top:1px solid #e6ebf1;">
#                         <div style="font-size:12px;color:#006b57;">
#                             <strong>Final Debt-to-Income (DSR)</strong>
#                             <span style="float:right;">
#                                 {dsr_val}
#                             </span>
#                         </div>
#                     </div>
#                     """,
#                     unsafe_allow_html=True,
#                 )

#                 if results.get("dsr") is not None:
#                     st.progress(
#                         min(max(results["dsr"] / DSR_THRESHOLD, 0.0), 1.0)
#                     )
#                     st.caption(
#                         f"{results['dsr']:.1f}% "
#                         f"(Demo threshold: {DSR_THRESHOLD:.0f}%)"
#                     )
#                 else:
#                     st.warning("Salary is required to calculate DSR.")

#             else:
#                 cash_flow = st.session_state.get("business_cash_flow", 0.0)
#                 profit = st.session_state.get("business_profit", 0.0)
#                 repayment = results["monthly_repayment"]

#                 st.markdown(
#                     f"""
#                     <div class="soft-card">
#                         <div class="metric-label">Business Affordability Chain</div>
#                         <br>
#                         <div style="font-size:11px;">
#                             <strong>Average Cash Flow</strong>
#                             <span style="float:right;">{money(cash_flow)}</span>
#                         </div>
#                         <hr style="border:none;border-top:1px solid #e6ebf1;">
#                         <div style="font-size:11px;">
#                             <strong>Profit</strong>
#                             <span style="float:right;">{money(profit)}</span>
#                         </div>
#                         <hr style="border:none;border-top:1px solid #e6ebf1;">
#                         <div style="font-size:11px;">
#                             <strong>Proposed Repayment</strong>
#                             <span style="float:right;">{money(repayment)}/mo</span>
#                         </div>
#                     </div>
#                     """,
#                     unsafe_allow_html=True,
#                 )

#                 st.markdown(
#                     '<div class="status-box status-info">'
#                     "Simplified POC rule: positive profit + positive cash flow "
#                     "and cash flow sufficient to cover proposed repayment."
#                     "</div>",
#                     unsafe_allow_html=True,
#                 )

#             st.markdown(
#                 f"""
#                 <div class="rule-note">
#                     ⚠ Repayment period ({repayment_period} months)
#                     is determined by lender/product policy.<br>
#                     ⚠ DSR threshold ({DSR_THRESHOLD:.0f}%) is a demo assumption —
#                     lender validation required.
#                 </div>
#                 """,
#                 unsafe_allow_html=True,
#             )

#     with right:
#         with st.container(border=True):
#             risk_class = (
#                 "pass"
#                 if results["repayment_risk"] == "LOW"
#                 else (
#                     "warn" if results["repayment_risk"] == "MEDIUM" else "fail"
#                 )
#             )

#             st.markdown(
#                 f"""
#                 <div style="display:flex;justify-content:space-between;align-items:center;">
#                     <div class="section-title" style="margin:0;">
#                         Repayment Risk & Qualitative Factors
#                     </div>
#                     <span class="badge {risk_class}">
#                         REPAYMENT RISK: {results["repayment_risk"]}
#                     </span>
#                 </div>
#                 """,
#                 unsafe_allow_html=True,
#             )

#             st.markdown("<br>", unsafe_allow_html=True)

#             for reason in results.get("risk_reasons", []):
#                 st.markdown(
#                     f"""
#                     <div style="font-size:11px;margin-bottom:10px;">
#                         <span style="color:#006b57;font-weight:700;">✓</span>
#                         {reason}
#                     </div>
#                     """,
#                     unsafe_allow_html=True,
#                 )

#             if results.get("thin_credit"):
#                 st.markdown(
#                     """
#                     <div class="status-box status-warn">
#                         ⚠ <strong>Thin formal credit history</strong><br>
#                         Risk assessment uses the other available indicators.
#                         Limited credit history should not automatically result
#                         in rejection in this POC.
#                     </div>
#                     """,
#                     unsafe_allow_html=True,
#                 )

#             st.markdown(
#                 f"""
#                 <div class="soft-card" style="margin-top:12px;">
#                     <div style="font-size:10px;color:#68788c;font-weight:700;">
#                         RISK RATIONALE
#                     </div>
#                     <div style="font-size:10px;color:#68788c;margin-top:5px;line-height:1.5;">
#                         {results.get("risk_rationale", "")}
#                     </div>
#                 </div>
#                 """,
#                 unsafe_allow_html=True,
#             )

#             st.markdown(
#                 """
#                 <div class="rule-note">
#                     ⚠ Illustrative POC risk model — not a lender-approved
#                     credit score. Replace the demo scoring logic with validated
#                     lender rules.
#                 </div>
#                 """,
#                 unsafe_allow_html=True,
#             )

#             st.markdown("<br>", unsafe_allow_html=True)
#             b1, b2 = st.columns([1, 2])
#             with b1:
#                 if st.button("← Back", use_container_width=True):
#                     st.session_state.step = 2
#                     st.rerun()
#             with b2:
#                 if st.button(
#                     "Generate Decision", type="primary", use_container_width=True
#                 ):
#                     st.session_state.step = 4
#                     st.session_state.verification_run = True
#                     st.rerun()