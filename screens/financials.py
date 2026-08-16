import streamlit as st
from utils.ui import render_progress


def safe_float(val, default=0.0):
    """Safely converts input to float, falling back to default if value is None or invalid."""
    if val is None:
        return float(default)
    try:
        return float(val)
    except (ValueError, TypeError):
        return float(default)


def safe_int(val, default=12):
    """Safely converts input to int, falling back to default if value is None or invalid."""
    if val is None:
        return int(default)
    try:
        return int(val)
    except (ValueError, TypeError):
        return int(default)


def screen_financials():
    render_progress()

    # Exact string match check prevents "Self-Employed" from triggering "Employed"
    applicant_type = st.session_state.get("applicant_type", "Salaried / Employed")
    is_salaried = applicant_type == "Salaried / Employed"

    profile_label = "Salaried" if is_salaried else "Business Owner"

    left, right = st.columns([1.7, 0.85], gap="large")

    with left:
        with st.container(border=True):
            st.markdown(
                f'<div class="section-title">Financial Status & Profile ({profile_label})</div>',
                unsafe_allow_html=True,
            )

            if is_salaried:
                c1, c2 = st.columns(2)

                # Safely resolve current numeric values
                current_salary = safe_float(
                    st.session_state.get("saved_salary")
                    if st.session_state.get("saved_salary") is not None
                    else st.session_state.get("salary")
                )

                current_debt = safe_float(
                    st.session_state.get("saved_existing_debt")
                    if st.session_state.get("saved_existing_debt") is not None
                    else st.session_state.get("existing_debt")
                )

                with c1:
                    salary = st.number_input(
                        "Monthly Net Salary (GHS)",
                        min_value=0.0,
                        step=100.0,
                        value=current_salary,
                        placeholder="Enter monthly net salary",
                        key="input_salary",
                    )

                    emp_type_options = ["Government", "Private / Corporate"]
                    saved_emp = st.session_state.get("saved_employment_type") or st.session_state.get("employment_type")
                    emp_index = emp_type_options.index(saved_emp) if saved_emp in emp_type_options else None

                    employment_type = st.radio(
                        "Employment Type",
                        emp_type_options,
                        index=emp_index,
                        horizontal=True,
                        key="input_employment_type",
                    )

                with c2:
                    existing_debt = st.number_input(
                        "Existing Monthly Debt Repayment (GHS)",
                        min_value=0.0,
                        step=50.0,
                        value=current_debt,
                        placeholder="Enter monthly debt repayment",
                        key="input_existing_debt",
                    )

                    tenure_options = ["Less than 6 months", "6 months", "1 year", "2 years", "3+ years"]
                    saved_tenure = st.session_state.get("saved_years_at_job") or st.session_state.get("years_at_job")
                    tenure_index = tenure_options.index(saved_tenure) if saved_tenure in tenure_options else None

                    years_at_job = st.selectbox(
                        "Years at Current Job",
                        tenure_options,
                        index=tenure_index,
                        placeholder="Select employment history",
                        key="input_years_at_job",
                    )

                credit_options = [
                    "No formal credit history",
                    "Limited credit history",
                    "Clean / satisfactory",
                    "Adverse / past delinquencies",
                ]
                saved_credit = st.session_state.get("saved_credit_history") or st.session_state.get("credit_history")
                credit_index = credit_options.index(saved_credit) if saved_credit in credit_options else None

                credit_history = st.selectbox(
                    "Credit History",
                    credit_options,
                    index=credit_index,
                    placeholder="Select credit history",
                    key="input_credit_history",
                )

            else:
                c1, c2 = st.columns(2)

                current_income = safe_float(
                    st.session_state.get("saved_business_income")
                    if st.session_state.get("saved_business_income") is not None
                    else st.session_state.get("business_income")
                )

                current_profit = safe_float(
                    st.session_state.get("saved_business_profit")
                    if st.session_state.get("saved_business_profit") is not None
                    else st.session_state.get("business_profit")
                )

                current_cash_flow = safe_float(
                    st.session_state.get("saved_business_cash_flow")
                    if st.session_state.get("saved_business_cash_flow") is not None
                    else st.session_state.get("business_cash_flow")
                )

                current_debt = safe_float(
                    st.session_state.get("saved_existing_debt")
                    if st.session_state.get("saved_existing_debt") is not None
                    else st.session_state.get("existing_debt")
                )

                with c1:
                    business_income = st.number_input(
                        "Average Monthly Business Income (GHS)",
                        min_value=0.0,
                        step=100.0,
                        value=current_income,
                        placeholder="Enter average monthly income",
                        key="input_business_income",
                    )
                    business_profit = st.number_input(
                        "Monthly Profit (GHS)",
                        min_value=0.0,
                        step=100.0,
                        value=current_profit,
                        placeholder="Enter monthly profit",
                        key="input_business_profit",
                    )

                with c2:
                    business_cash_flow = st.number_input(
                        "Average Monthly Cash Flow (GHS)",
                        min_value=0.0,
                        step=100.0,
                        value=current_cash_flow,
                        placeholder="Enter average monthly cash flow",
                        key="input_business_cash_flow",
                    )
                    existing_debt = st.number_input(
                        "Existing Monthly Debt Repayment (GHS)",
                        min_value=0.0,
                        step=50.0,
                        value=current_debt,
                        placeholder="Enter monthly debt repayment",
                        key="input_existing_debt",
                    )

                credit_options = [
                    "No formal credit history",
                    "Limited credit history",
                    "Clean / satisfactory",
                    "Adverse / past delinquencies",
                ]
                saved_credit = st.session_state.get("saved_credit_history") or st.session_state.get("credit_history")
                credit_index = credit_options.index(saved_credit) if saved_credit in credit_options else None

                credit_history = st.selectbox(
                    "Credit Character / Credit History",
                    credit_options,
                    index=credit_index,
                    placeholder="Select credit history",
                    key="input_credit_history",
                )

                guarantor_options = ["Yes", "No"]
                saved_guarantor = st.session_state.get("guarantor_available")
                guarantor_index = guarantor_options.index(saved_guarantor) if saved_guarantor in guarantor_options else None

                guarantor_available = st.radio(
                    "Guarantor Available?",
                    guarantor_options,
                    index=guarantor_index,
                    horizontal=True,
                    key="input_guarantor_available",
                )

                if guarantor_available == "Yes":
                    g_cred_options = ["Clean / satisfactory", "Unknown / not verified", "Adverse"]
                    saved_g_cred = st.session_state.get("guarantor_credit")
                    g_cred_index = g_cred_options.index(saved_g_cred) if saved_g_cred in g_cred_options else None

                    guarantor_credit = st.selectbox(
                        "Guarantor Credit Status",
                        g_cred_options,
                        index=g_cred_index,
                        placeholder="Select guarantor credit status",
                        key="input_guarantor_credit",
                    )
                else:
                    guarantor_credit = None

            st.markdown("<br>", unsafe_allow_html=True)

            current_repayment_period = safe_int(
                st.session_state.get("saved_repayment_period")
                if st.session_state.get("saved_repayment_period") is not None
                else st.session_state.get("repayment_period"),
                default=12,
            )

            repayment_period = st.number_input(
                "Lender-configured Repayment Period (months)",
                min_value=1,
                max_value=60,
                step=1,
                value=current_repayment_period,
                placeholder="Enter lender-configured period",
                key="input_repayment_period",
                help="The lender/product policy determines this value.",
            )

            st.markdown(
                '<div class="small-note">Repayment period is entered/configured by the lender. '
                'The POC uses it to calculate the proposed monthly repayment.</div>',
                unsafe_allow_html=True,
            )

            # --- Validation Checks ---
            if is_salaried:
                required = [
                    employment_type,
                    years_at_job,
                    credit_history,
                    repayment_period,
                ]
                valid = all(v is not None for v in required) and salary > 0
            else:
                required = [
                    business_income,
                    business_profit,
                    business_cash_flow,
                    credit_history,
                    guarantor_available,
                    repayment_period,
                ]
                if guarantor_available == "Yes":
                    required.append(guarantor_credit)
                valid = all(v is not None for v in required) and (business_income > 0 or business_profit > 0)

            st.markdown("<br>", unsafe_allow_html=True)
            b1, b2 = st.columns([1, 2])

            with b1:
                if st.button("← Back", use_container_width=True):
                    st.session_state.step = 1
                    st.rerun()

            with b2:
                if st.button(
                    "Analyze Risk Assessment",
                    type="primary",
                    use_container_width=True,
                    disabled=not valid,
                ):
                    if is_salaried:
                        st.session_state["saved_salary"] = salary
                        st.session_state["saved_employment_type"] = employment_type
                        st.session_state["saved_years_at_job"] = years_at_job
                    else:
                        st.session_state["saved_business_income"] = business_income
                        st.session_state["saved_business_profit"] = business_profit
                        st.session_state["saved_business_cash_flow"] = business_cash_flow
                        st.session_state["guarantor_available"] = guarantor_available
                        st.session_state["guarantor_credit"] = guarantor_credit

                    st.session_state["saved_existing_debt"] = existing_debt
                    st.session_state["saved_credit_history"] = credit_history
                    st.session_state["saved_repayment_period"] = repayment_period

                    st.session_state.assessment_run = True
                    st.session_state.step = 3
                    st.rerun()

            if not valid:
                st.caption("Complete all required financial fields to continue.")

    with right:
        with st.container(border=True):
            st.markdown(
                '<div class="section-title">Required Verification Docs</div>',
                unsafe_allow_html=True,
            )
            st.caption("Upload supporting documents. Uploading does not mean verified.")

            if is_salaried:
                st.session_state.payslip = st.file_uploader(
                    "Payslips (Last 3 Months)",
                    type=["pdf", "png", "jpg", "jpeg"],
                    key="payslip_uploader",
                )
                st.session_state.employment_proof = st.file_uploader(
                    "Proof of Employment",
                    type=["pdf", "png", "jpg", "jpeg"],
                    key="employment_uploader",
                )
            else:
                st.session_state.business_proof = st.file_uploader(
                    "Business Financial Evidence",
                    type=["pdf", "png", "jpg", "jpeg", "xlsx", "csv"],
                    key="business_uploader",
                )

            st.session_state.rental_proof = st.file_uploader(
                "Rental / Tenancy Evidence",
                type=["pdf", "png", "jpg", "jpeg"],
                key="rental_uploader",
            )

            if not is_salaried and st.session_state.get("guarantor_available") == "Yes":
                st.session_state.guarantor_proof = st.file_uploader(
                    "Guarantor Evidence",
                    type=["pdf", "png", "jpg", "jpeg"],
                    key="guarantor_uploader",
                )

            st.markdown(
                '<div class="rule-note">Uploaded documents remain '
                '<strong>Verification Pending</strong> in this POC.</div>',
                unsafe_allow_html=True,
            )













#this code works but provides input of unsalaried applicant under financials as salaried applicant
# import streamlit as st
# from utils.ui import render_progress


# def safe_float(val, default=0.0):
#     """Safely converts input to float, falling back to default if value is None or invalid."""
#     if val is None:
#         return float(default)
#     try:
#         return float(val)
#     except (ValueError, TypeError):
#         return float(default)


# def safe_int(val, default=12):
#     """Safely converts input to int, falling back to default if value is None or invalid."""
#     if val is None:
#         return int(default)
#     try:
#         return int(val)
#     except (ValueError, TypeError):
#         return int(default)


# def screen_financials():
#     render_progress()

#     # Safely extract applicant_type string
#     applicant_type = str(st.session_state.get("applicant_type", "Salaried / Employed"))
#     is_salaried = "salaried" in applicant_type.lower() or "employed" in applicant_type.lower()

#     profile_label = "Salaried" if is_salaried else "Business Owner"

#     left, right = st.columns([1.7, 0.85], gap="large")

#     with left:
#         with st.container(border=True):
#             st.markdown(
#                 f'<div class="section-title">Financial Status & Profile ({profile_label})</div>',
#                 unsafe_allow_html=True,
#             )

#             if is_salaried:
#                 c1, c2 = st.columns(2)

#                 # Safely resolve current numeric values
#                 current_salary = safe_float(
#                     st.session_state.get("saved_salary")
#                     if st.session_state.get("saved_salary") is not None
#                     else st.session_state.get("salary")
#                 )

#                 current_debt = safe_float(
#                     st.session_state.get("saved_existing_debt")
#                     if st.session_state.get("saved_existing_debt") is not None
#                     else st.session_state.get("existing_debt")
#                 )

#                 with c1:
#                     salary = st.number_input(
#                         "Monthly Net Salary (GHS)",
#                         min_value=0.0,
#                         step=100.0,
#                         value=current_salary,
#                         placeholder="Enter monthly net salary",
#                         key="input_salary",
#                     )

#                     emp_type_options = ["Government", "Private / Corporate"]
#                     saved_emp = st.session_state.get("saved_employment_type") or st.session_state.get("employment_type")
#                     emp_index = emp_type_options.index(saved_emp) if saved_emp in emp_type_options else None

#                     employment_type = st.radio(
#                         "Employment Type",
#                         emp_type_options,
#                         index=emp_index,
#                         horizontal=True,
#                         key="input_employment_type",
#                     )

#                 with c2:
#                     existing_debt = st.number_input(
#                         "Existing Monthly Debt Repayment (GHS)",
#                         min_value=0.0,
#                         step=50.0,
#                         value=current_debt,
#                         placeholder="Enter monthly debt repayment",
#                         key="input_existing_debt",
#                     )

#                     tenure_options = ["Less than 6 months", "6 months", "1 year", "2 years", "3+ years"]
#                     saved_tenure = st.session_state.get("saved_years_at_job") or st.session_state.get("years_at_job")
#                     tenure_index = tenure_options.index(saved_tenure) if saved_tenure in tenure_options else None

#                     years_at_job = st.selectbox(
#                         "Years at Current Job",
#                         tenure_options,
#                         index=tenure_index,
#                         placeholder="Select employment history",
#                         key="input_years_at_job",
#                     )

#                 credit_options = [
#                     "No formal credit history",
#                     "Limited credit history",
#                     "Clean / satisfactory",
#                     "Adverse / past delinquencies",
#                 ]
#                 saved_credit = st.session_state.get("saved_credit_history") or st.session_state.get("credit_history")
#                 credit_index = credit_options.index(saved_credit) if saved_credit in credit_options else None

#                 credit_history = st.selectbox(
#                     "Credit History",
#                     credit_options,
#                     index=credit_index,
#                     placeholder="Select credit history",
#                     key="input_credit_history",
#                 )

#             else:
#                 c1, c2 = st.columns(2)

#                 current_income = safe_float(
#                     st.session_state.get("saved_business_income")
#                     if st.session_state.get("saved_business_income") is not None
#                     else st.session_state.get("business_income")
#                 )

#                 current_profit = safe_float(
#                     st.session_state.get("saved_business_profit")
#                     if st.session_state.get("saved_business_profit") is not None
#                     else st.session_state.get("business_profit")
#                 )

#                 current_cash_flow = safe_float(
#                     st.session_state.get("saved_business_cash_flow")
#                     if st.session_state.get("saved_business_cash_flow") is not None
#                     else st.session_state.get("business_cash_flow")
#                 )

#                 current_debt = safe_float(
#                     st.session_state.get("saved_existing_debt")
#                     if st.session_state.get("saved_existing_debt") is not None
#                     else st.session_state.get("existing_debt")
#                 )

#                 with c1:
#                     business_income = st.number_input(
#                         "Average Monthly Business Income (GHS)",
#                         min_value=0.0,
#                         step=100.0,
#                         value=current_income,
#                         placeholder="Enter average monthly income",
#                         key="input_business_income",
#                     )
#                     business_profit = st.number_input(
#                         "Monthly Profit (GHS)",
#                         min_value=0.0,
#                         step=100.0,
#                         value=current_profit,
#                         placeholder="Enter monthly profit",
#                         key="input_business_profit",
#                     )

#                 with c2:
#                     business_cash_flow = st.number_input(
#                         "Average Monthly Cash Flow (GHS)",
#                         min_value=0.0,
#                         step=100.0,
#                         value=current_cash_flow,
#                         placeholder="Enter average monthly cash flow",
#                         key="input_business_cash_flow",
#                     )
#                     existing_debt = st.number_input(
#                         "Existing Monthly Debt Repayment (GHS)",
#                         min_value=0.0,
#                         step=50.0,
#                         value=current_debt,
#                         placeholder="Enter monthly debt repayment",
#                         key="input_existing_debt",
#                     )

#                 credit_options = [
#                     "No formal credit history",
#                     "Limited credit history",
#                     "Clean / satisfactory",
#                     "Adverse / past delinquencies",
#                 ]
#                 saved_credit = st.session_state.get("saved_credit_history") or st.session_state.get("credit_history")
#                 credit_index = credit_options.index(saved_credit) if saved_credit in credit_options else None

#                 credit_history = st.selectbox(
#                     "Credit Character / Credit History",
#                     credit_options,
#                     index=credit_index,
#                     placeholder="Select credit history",
#                     key="input_credit_history",
#                 )

#                 guarantor_options = ["Yes", "No"]
#                 saved_guarantor = st.session_state.get("guarantor_available")
#                 guarantor_index = guarantor_options.index(saved_guarantor) if saved_guarantor in guarantor_options else None

#                 guarantor_available = st.radio(
#                     "Guarantor Available?",
#                     guarantor_options,
#                     index=guarantor_index,
#                     horizontal=True,
#                     key="input_guarantor_available",
#                 )

#                 if guarantor_available == "Yes":
#                     g_cred_options = ["Clean / satisfactory", "Unknown / not verified", "Adverse"]
#                     saved_g_cred = st.session_state.get("guarantor_credit")
#                     g_cred_index = g_cred_options.index(saved_g_cred) if saved_g_cred in g_cred_options else None

#                     guarantor_credit = st.selectbox(
#                         "Guarantor Credit Status",
#                         g_cred_options,
#                         index=g_cred_index,
#                         placeholder="Select guarantor credit status",
#                         key="input_guarantor_credit",
#                     )
#                 else:
#                     guarantor_credit = None

#             st.markdown("<br>", unsafe_allow_html=True)

#             current_repayment_period = safe_int(
#                 st.session_state.get("saved_repayment_period")
#                 if st.session_state.get("saved_repayment_period") is not None
#                 else st.session_state.get("repayment_period"),
#                 default=12,
#             )

#             repayment_period = st.number_input(
#                 "Lender-configured Repayment Period (months)",
#                 min_value=1,
#                 max_value=60,
#                 step=1,
#                 value=current_repayment_period,
#                 placeholder="Enter lender-configured period",
#                 key="input_repayment_period",
#                 help="The lender/product policy determines this value.",
#             )

#             st.markdown(
#                 '<div class="small-note">Repayment period is entered/configured by the lender. '
#                 'The POC uses it to calculate the proposed monthly repayment.</div>',
#                 unsafe_allow_html=True,
#             )

#             # --- Validation Checks ---
#             if is_salaried:
#                 required = [
#                     employment_type,
#                     years_at_job,
#                     credit_history,
#                     repayment_period,
#                 ]
#                 valid = all(v is not None for v in required) and salary > 0
#             else:
#                 required = [
#                     business_income,
#                     business_profit,
#                     business_cash_flow,
#                     credit_history,
#                     guarantor_available,
#                     repayment_period,
#                 ]
#                 if guarantor_available == "Yes":
#                     required.append(guarantor_credit)
#                 valid = all(v is not None for v in required)

#             st.markdown("<br>", unsafe_allow_html=True)
#             b1, b2 = st.columns([1, 2])

#             with b1:
#                 if st.button("← Back", use_container_width=True):
#                     st.session_state.step = 1
#                     st.rerun()

#             with b2:
#                 if st.button(
#                     "Analyze Risk Assessment",
#                     type="primary",
#                     use_container_width=True,
#                     disabled=not valid,
#                 ):
#                     if is_salaried:
#                         st.session_state["saved_salary"] = salary
#                         st.session_state["saved_employment_type"] = employment_type
#                         st.session_state["saved_years_at_job"] = years_at_job
#                     else:
#                         st.session_state["saved_business_income"] = business_income
#                         st.session_state["saved_business_profit"] = business_profit
#                         st.session_state["saved_business_cash_flow"] = business_cash_flow
#                         st.session_state["guarantor_available"] = guarantor_available
#                         st.session_state["guarantor_credit"] = guarantor_credit

#                     st.session_state["saved_existing_debt"] = existing_debt
#                     st.session_state["saved_credit_history"] = credit_history
#                     st.session_state["saved_repayment_period"] = repayment_period

#                     st.session_state.assessment_run = True
#                     st.session_state.step = 3
#                     st.rerun()

#             if not valid:
#                 st.caption("Complete all required financial fields and ensure salary/income is greater than 0 to continue.")

#     with right:
#         with st.container(border=True):
#             st.markdown(
#                 '<div class="section-title">Required Verification Docs</div>',
#                 unsafe_allow_html=True,
#             )
#             st.caption("Upload supporting documents. Uploading does not mean verified.")

#             if is_salaried:
#                 st.session_state.payslip = st.file_uploader(
#                     "Payslips (Last 3 Months)",
#                     type=["pdf", "png", "jpg", "jpeg"],
#                     key="payslip_uploader",
#                 )
#                 st.session_state.employment_proof = st.file_uploader(
#                     "Proof of Employment",
#                     type=["pdf", "png", "jpg", "jpeg"],
#                     key="employment_uploader",
#                 )
#             else:
#                 st.session_state.business_proof = st.file_uploader(
#                     "Business Financial Evidence",
#                     type=["pdf", "png", "jpg", "jpeg", "xlsx", "csv"],
#                     key="business_uploader",
#                 )

#             st.session_state.rental_proof = st.file_uploader(
#                 "Rental / Tenancy Evidence",
#                 type=["pdf", "png", "jpg", "jpeg"],
#                 key="rental_uploader",
#             )

#             if not is_salaried and st.session_state.get("guarantor_available") == "Yes":
#                 st.session_state.guarantor_proof = st.file_uploader(
#                     "Guarantor Evidence",
#                     type=["pdf", "png", "jpg", "jpeg"],
#                     key="guarantor_uploader",
#                 )

#             st.markdown(
#                 '<div class="rule-note">Uploaded documents remain '
#                 '<strong>Verification Pending</strong> in this POC.</div>',
#                 unsafe_allow_html=True,
#             )










#GAVE A TypeError: float() argument must be a string or a real number, not 'NoneType' I think for the salary amount
# import streamlit as st
# from utils.ui import render_progress


# def screen_financials():
#     render_progress()

#     # Safely extract applicant_type string
#     applicant_type = str(st.session_state.get("applicant_type", "Salaried / Employed"))
#     is_salaried = "salaried" in applicant_type.lower() or "employed" in applicant_type.lower()

#     profile_label = "Salaried" if is_salaried else "Business Owner"

#     left, right = st.columns([1.7, 0.85], gap="large")

#     with left:
#         with st.container(border=True):
#             st.markdown(
#                 f'<div class="section-title">Financial Status & Profile ({profile_label})</div>',
#                 unsafe_allow_html=True,
#             )

#             if is_salaried:
#                 c1, c2 = st.columns(2)

#                 with c1:
#                     salary = st.number_input(
#                         "Monthly Net Salary (GHS)",
#                         min_value=0.0,
#                         step=100.0,
#                         value=float(st.session_state.get("saved_salary", st.session_state.get("salary", 0.0))),
#                         placeholder="Enter monthly net salary",
#                         key="input_salary",
#                     )
#                     emp_type_options = ["Government", "Private / Corporate"]
#                     saved_emp = st.session_state.get("saved_employment_type", st.session_state.get("employment_type"))
#                     emp_index = emp_type_options.index(saved_emp) if saved_emp in emp_type_options else None

#                     employment_type = st.radio(
#                         "Employment Type",
#                         emp_type_options,
#                         index=emp_index,
#                         horizontal=True,
#                         key="input_employment_type",
#                     )

#                 with c2:
#                     existing_debt = st.number_input(
#                         "Existing Monthly Debt Repayment (GHS)",
#                         min_value=0.0,
#                         step=50.0,
#                         value=float(st.session_state.get("saved_existing_debt", st.session_state.get("existing_debt", 0.0))),
#                         placeholder="Enter monthly debt repayment",
#                         key="input_existing_debt",
#                     )
#                     tenure_options = ["Less than 6 months", "6 months", "1 year", "2 years", "3+ years"]
#                     saved_tenure = st.session_state.get("saved_years_at_job", st.session_state.get("years_at_job"))
#                     tenure_index = tenure_options.index(saved_tenure) if saved_tenure in tenure_options else None

#                     years_at_job = st.selectbox(
#                         "Years at Current Job",
#                         tenure_options,
#                         index=tenure_index,
#                         placeholder="Select employment history",
#                         key="input_years_at_job",
#                     )

#                 credit_options = [
#                     "No formal credit history",
#                     "Limited credit history",
#                     "Clean / satisfactory",
#                     "Adverse / past delinquencies",
#                 ]
#                 saved_credit = st.session_state.get("saved_credit_history", st.session_state.get("credit_history"))
#                 credit_index = credit_options.index(saved_credit) if saved_credit in credit_options else None

#                 credit_history = st.selectbox(
#                     "Credit History",
#                     credit_options,
#                     index=credit_index,
#                     placeholder="Select credit history",
#                     key="input_credit_history",
#                 )

#             else:
#                 c1, c2 = st.columns(2)

#                 with c1:
#                     business_income = st.number_input(
#                         "Average Monthly Business Income (GHS)",
#                         min_value=0.0,
#                         step=100.0,
#                         value=float(st.session_state.get("saved_business_income", st.session_state.get("business_income", 0.0))),
#                         placeholder="Enter average monthly income",
#                         key="input_business_income",
#                     )
#                     business_profit = st.number_input(
#                         "Monthly Profit (GHS)",
#                         min_value=0.0,
#                         step=100.0,
#                         value=float(st.session_state.get("saved_business_profit", st.session_state.get("business_profit", 0.0))),
#                         placeholder="Enter monthly profit",
#                         key="input_business_profit",
#                     )

#                 with c2:
#                     business_cash_flow = st.number_input(
#                         "Average Monthly Cash Flow (GHS)",
#                         min_value=0.0,
#                         step=100.0,
#                         value=float(st.session_state.get("saved_business_cash_flow", st.session_state.get("business_cash_flow", 0.0))),
#                         placeholder="Enter average monthly cash flow",
#                         key="input_business_cash_flow",
#                     )
#                     existing_debt = st.number_input(
#                         "Existing Monthly Debt Repayment (GHS)",
#                         min_value=0.0,
#                         step=50.0,
#                         value=float(st.session_state.get("saved_existing_debt", st.session_state.get("existing_debt", 0.0))),
#                         placeholder="Enter monthly debt repayment",
#                         key="input_existing_debt",
#                     )

#                 credit_options = [
#                     "No formal credit history",
#                     "Limited credit history",
#                     "Clean / satisfactory",
#                     "Adverse / past delinquencies",
#                 ]
#                 saved_credit = st.session_state.get("saved_credit_history", st.session_state.get("credit_history"))
#                 credit_index = credit_options.index(saved_credit) if saved_credit in credit_options else None

#                 credit_history = st.selectbox(
#                     "Credit Character / Credit History",
#                     credit_options,
#                     index=credit_index,
#                     placeholder="Select credit history",
#                     key="input_credit_history",
#                 )

#                 guarantor_options = ["Yes", "No"]
#                 saved_guarantor = st.session_state.get("guarantor_available")
#                 guarantor_index = guarantor_options.index(saved_guarantor) if saved_guarantor in guarantor_options else None

#                 guarantor_available = st.radio(
#                     "Guarantor Available?",
#                     guarantor_options,
#                     index=guarantor_index,
#                     horizontal=True,
#                     key="input_guarantor_available",
#                 )

#                 if guarantor_available == "Yes":
#                     g_cred_options = ["Clean / satisfactory", "Unknown / not verified", "Adverse"]
#                     saved_g_cred = st.session_state.get("guarantor_credit")
#                     g_cred_index = g_cred_options.index(saved_g_cred) if saved_g_cred in g_cred_options else None

#                     guarantor_credit = st.selectbox(
#                         "Guarantor Credit Status",
#                         g_cred_options,
#                         index=g_cred_index,
#                         placeholder="Select guarantor credit status",
#                         key="input_guarantor_credit",
#                     )
#                 else:
#                     guarantor_credit = None

#             st.markdown("<br>", unsafe_allow_html=True)

#             repayment_period = st.number_input(
#                 "Lender-configured Repayment Period (months)",
#                 min_value=1,
#                 max_value=60,
#                 step=1,
#                 value=int(st.session_state.get("saved_repayment_period", st.session_state.get("repayment_period", 12))),
#                 placeholder="Enter lender-configured period",
#                 key="input_repayment_period",
#                 help="The lender/product policy determines this value.",
#             )

#             st.markdown(
#                 '<div class="small-note">Repayment period is entered/configured by the lender. '
#                 'The POC uses it to calculate the proposed monthly repayment.</div>',
#                 unsafe_allow_html=True,
#             )

#             # --- Validation Checks ---
#             if is_salaried:
#                 required = [
#                     employment_type,
#                     years_at_job,
#                     credit_history,
#                     repayment_period,
#                 ]
#                 valid = all(v is not None for v in required) and salary > 0
#             else:
#                 required = [
#                     business_income,
#                     business_profit,
#                     business_cash_flow,
#                     credit_history,
#                     guarantor_available,
#                     repayment_period,
#                 ]
#                 if guarantor_available == "Yes":
#                     required.append(guarantor_credit)
#                 valid = all(v is not None for v in required)

#             st.markdown("<br>", unsafe_allow_html=True)
#             b1, b2 = st.columns([1, 2])

#             with b1:
#                 if st.button("← Back", use_container_width=True):
#                     st.session_state.step = 1
#                     st.rerun()

#             with b2:
#                 if st.button(
#                     "Analyze Risk Assessment",
#                     type="primary",
#                     use_container_width=True,
#                     disabled=not valid,
#                 ):
#                     # Save inputs permanently to session_state prior to step transition
#                     if is_salaried:
#                         st.session_state["saved_salary"] = salary
#                         st.session_state["saved_employment_type"] = employment_type
#                         st.session_state["saved_years_at_job"] = years_at_job
#                     else:
#                         st.session_state["saved_business_income"] = business_income
#                         st.session_state["saved_business_profit"] = business_profit
#                         st.session_state["saved_business_cash_flow"] = business_cash_flow
#                         st.session_state["guarantor_available"] = guarantor_available
#                         st.session_state["guarantor_credit"] = guarantor_credit

#                     st.session_state["saved_existing_debt"] = existing_debt
#                     st.session_state["saved_credit_history"] = credit_history
#                     st.session_state["saved_repayment_period"] = repayment_period

#                     st.session_state.assessment_run = True
#                     st.session_state.step = 3
#                     st.rerun()

#             if not valid:
#                 st.caption("Complete all required financial fields and ensure salary/income is greater than 0 to continue.")

#     with right:
#         with st.container(border=True):
#             st.markdown(
#                 '<div class="section-title">Required Verification Docs</div>',
#                 unsafe_allow_html=True,
#             )
#             st.caption("Upload supporting documents. Uploading does not mean verified.")

#             if is_salaried:
#                 st.session_state.payslip = st.file_uploader(
#                     "Payslips (Last 3 Months)",
#                     type=["pdf", "png", "jpg", "jpeg"],
#                     key="payslip_uploader",
#                 )
#                 st.session_state.employment_proof = st.file_uploader(
#                     "Proof of Employment",
#                     type=["pdf", "png", "jpg", "jpeg"],
#                     key="employment_uploader",
#                 )
#             else:
#                 st.session_state.business_proof = st.file_uploader(
#                     "Business Financial Evidence",
#                     type=["pdf", "png", "jpg", "jpeg", "xlsx", "csv"],
#                     key="business_uploader",
#                 )

#             st.session_state.rental_proof = st.file_uploader(
#                 "Rental / Tenancy Evidence",
#                 type=["pdf", "png", "jpg", "jpeg"],
#                 key="rental_uploader",
#             )

#             if not is_salaried and st.session_state.get("guarantor_available") == "Yes":
#                 st.session_state.guarantor_proof = st.file_uploader(
#                     "Guarantor Evidence",
#                     type=["pdf", "png", "jpg", "jpeg"],
#                     key="guarantor_uploader",
#                 )

#             st.markdown(
#                 '<div class="rule-note">Uploaded documents remain '
#                 '<strong>Verification Pending</strong> in this POC.</div>',
#                 unsafe_allow_html=True,
#             )










#seems this is causing the issue with the output under the explanatory types
# import streamlit as st
# from utils.ui import render_progress


# def screen_financials():
#     render_progress()

#     left, right = st.columns([1.7, 0.85], gap="large")

#     with left:
#         with st.container(border=True):
#             profile_label = (
#                 "Salaried" if st.session_state.applicant_type == "Salaried / Employed"
#                 else "Business Owner"
#             )

#             st.markdown(
#                 f'<div class="section-title">Financial Status & Profile ({profile_label})</div>',
#                 unsafe_allow_html=True,
#             )

#             if st.session_state.applicant_type == "Salaried / Employed":
#                 c1, c2 = st.columns(2)

#                 with c1:
#                     st.number_input(
#                         "Monthly Net Salary (GHS)",
#                         min_value=0.0,
#                         step=100.0,
#                         value=st.session_state.salary,
#                         placeholder="Enter monthly net salary",
#                         key="salary",
#                     )
#                     st.radio(
#                         "Employment Type",
#                         ["Government", "Private / Corporate"],
#                         index=None,
#                         horizontal=True,
#                         key="employment_type",
#                     )

#                 with c2:
#                     st.number_input(
#                         "Existing Monthly Debt Repayment (GHS)",
#                         min_value=0.0,
#                         step=50.0,
#                         value=st.session_state.existing_debt,
#                         placeholder="Enter monthly debt repayment",
#                         key="existing_debt",
#                     )
#                     st.selectbox(
#                         "Years at Current Job",
#                         ["Less than 6 months", "6 months", "1 year", "2 years", "3+ years"],
#                         index=None,
#                         placeholder="Select employment history",
#                         key="years_at_job",
#                     )

#                 st.selectbox(
#                     "Credit History",
#                     [
#                         "No formal credit history",
#                         "Limited credit history",
#                         "Clean / satisfactory",
#                         "Adverse / past delinquencies",
#                     ],
#                     index=None,
#                     placeholder="Select credit history",
#                     key="credit_history",
#                 )

#             else:
#                 c1, c2 = st.columns(2)

#                 with c1:
#                     st.number_input(
#                         "Average Monthly Business Income (GHS)",
#                         min_value=0.0,
#                         step=100.0,
#                         value=st.session_state.business_income,
#                         placeholder="Enter average monthly income",
#                         key="business_income",
#                     )
#                     st.number_input(
#                         "Monthly Profit (GHS)",
#                         min_value=0.0,
#                         step=100.0,
#                         value=st.session_state.business_profit,
#                         placeholder="Enter monthly profit",
#                         key="business_profit",
#                     )

#                 with c2:
#                     st.number_input(
#                         "Average Monthly Cash Flow (GHS)",
#                         min_value=0.0,
#                         step=100.0,
#                         value=st.session_state.business_cash_flow,
#                         placeholder="Enter average monthly cash flow",
#                         key="business_cash_flow",
#                     )
#                     st.number_input(
#                         "Existing Monthly Debt Repayment (GHS)",
#                         min_value=0.0,
#                         step=50.0,
#                         value=st.session_state.existing_debt,
#                         placeholder="Enter monthly debt repayment",
#                         key="existing_debt",
#                     )

#                 st.selectbox(
#                     "Credit Character / Credit History",
#                     [
#                         "No formal credit history",
#                         "Limited credit history",
#                         "Clean / satisfactory",
#                         "Adverse / past delinquencies",
#                     ],
#                     index=None,
#                     placeholder="Select credit history",
#                     key="credit_history",
#                 )

#                 st.radio(
#                     "Guarantor Available?",
#                     ["Yes", "No"],
#                     index=None,
#                     horizontal=True,
#                     key="guarantor_available",
#                 )

#                 if st.session_state.guarantor_available == "Yes":
#                     st.selectbox(
#                         "Guarantor Credit Status",
#                         ["Clean / satisfactory", "Unknown / not verified", "Adverse"],
#                         index=None,
#                         placeholder="Select guarantor credit status",
#                         key="guarantor_credit",
#                     )

#             st.markdown("<br>", unsafe_allow_html=True)

#             st.number_input(
#                 "Lender-configured Repayment Period (months)",
#                 min_value=1,
#                 max_value=60,
#                 step=1,
#                 value=st.session_state.repayment_period,
#                 placeholder="Enter lender-configured period",
#                 key="repayment_period",
#                 help="The lender/product policy determines this value.",
#             )

#             st.markdown(
#                 '<div class="small-note">Repayment period is entered/configured by the lender. '
#                 'The POC uses it to calculate the proposed monthly repayment.</div>',
#                 unsafe_allow_html=True,
#             )

#             if st.session_state.applicant_type == "Salaried / Employed":
#                 required = [
#                     st.session_state.salary,
#                     st.session_state.existing_debt,
#                     st.session_state.employment_type,
#                     st.session_state.years_at_job,
#                     st.session_state.credit_history,
#                     st.session_state.repayment_period,
#                 ]
#             else:
#                 required = [
#                     st.session_state.business_income,
#                     st.session_state.business_profit,
#                     st.session_state.business_cash_flow,
#                     st.session_state.existing_debt,
#                     st.session_state.credit_history,
#                     st.session_state.guarantor_available,
#                     st.session_state.repayment_period,
#                 ]
#                 if st.session_state.guarantor_available == "Yes":
#                     required.append(st.session_state.guarantor_credit)

#             valid = all(value is not None for value in required)

#             st.markdown("<br>", unsafe_allow_html=True)
#             b1, b2 = st.columns([1, 2])

#             with b1:
#                 if st.button("← Back", use_container_width=True):
#                     st.session_state.step = 1
#                     st.rerun()

#             with b2:
#                 if st.button(
#                     "Analyze Risk Assessment",
#                     type="primary",
#                     use_container_width=True,
#                     disabled=not valid,
#                 ):
#                     st.session_state.assessment_run = True
#                     st.session_state.step = 3
#                     st.rerun()

#             if not valid:
#                 st.caption("Complete the required financial fields to continue.")

#     with right:
#         with st.container(border=True):
#             st.markdown(
#                 '<div class="section-title">Required Verification Docs</div>',
#                 unsafe_allow_html=True,
#             )
#             st.caption("Upload supporting documents. Uploading does not mean verified.")

#             if st.session_state.applicant_type == "Salaried / Employed":
#                 st.session_state.payslip = st.file_uploader(
#                     "Payslips (Last 3 Months)",
#                     type=["pdf", "png", "jpg", "jpeg"],
#                     key="payslip_uploader",
#                 )
#                 st.session_state.employment_proof = st.file_uploader(
#                     "Proof of Employment",
#                     type=["pdf", "png", "jpg", "jpeg"],
#                     key="employment_uploader",
#                 )
#             else:
#                 st.session_state.business_proof = st.file_uploader(
#                     "Business Financial Evidence",
#                     type=["pdf", "png", "jpg", "jpeg", "xlsx", "csv"],
#                     key="business_uploader",
#                 )

#             st.session_state.rental_proof = st.file_uploader(
#                 "Rental / Tenancy Evidence",
#                 type=["pdf", "png", "jpg", "jpeg"],
#                 key="rental_uploader",
#             )

#             if (
#                 st.session_state.applicant_type == "Business Owner / Self-Employed"
#                 and st.session_state.guarantor_available == "Yes"
#             ):
#                 st.session_state.guarantor_proof = st.file_uploader(
#                     "Guarantor Evidence",
#                     type=["pdf", "png", "jpg", "jpeg"],
#                     key="guarantor_uploader",
#                 )

#             st.markdown(
#                 '<div class="rule-note">Uploaded documents remain '
#                 '<strong>Verification Pending</strong> in this POC.</div>',
#                 unsafe_allow_html=True,
#             )
