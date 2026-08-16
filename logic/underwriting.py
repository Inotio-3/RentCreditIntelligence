"""Underwriting calculations and decision logic with robust session state fallbacks."""

import streamlit as st
from config import DSR_THRESHOLD
from utils.helpers import calculate_rent_advance_limit, money, parse_tenancy_months


def get_state_val(keys, default):
    """Safely retrieves the first non-None, non-empty value across multiple session state key aliases."""
    for key in keys:
        if key in st.session_state:
            val = st.session_state[key]
            if val is not None and val != "":
                return val
    return default


def calculate_assessment():
    """Calculates risk, affordability, and loan terms using multi-key session state retrieval."""

    # --- 1. Retrieve Financial Inputs Safely Across Widget Aliases ---
    monthly_rent = float(
        get_state_val(["saved_monthly_rent", "input_monthly_rent", "monthly_rent"], 0.0)
    )

    advance = float(
        get_state_val(["saved_advance_amount", "input_advance_amount", "advance_amount"], 0.0)
    )

    tenancy_duration = get_state_val(
        ["saved_tenancy_duration", "input_tenancy_duration", "tenancy_duration"], "12 months"
    )

    repayment_period = max(
        int(
            get_state_val(
                ["saved_repayment_period", "input_repayment_period", "repayment_period"],
                12,
            )
        ),
        1,
    )

    salary = float(
        get_state_val(["saved_salary", "input_salary", "salary"], 0.0)
    )

    existing_debt = float(
        get_state_val(["saved_existing_debt", "input_existing_debt", "existing_debt"], 0.0)
    )

    # Calculate monthly installments & total commitment
    monthly_repayment = advance / repayment_period if repayment_period > 0 else advance
    total_monthly_debt = existing_debt + monthly_repayment

    # --- 2. Calculate Rent-Advance Eligibility Cap ---
    tenancy_months = parse_tenancy_months(tenancy_duration) if tenancy_duration else 0
    allowed_months, maximum_advance = calculate_rent_advance_limit(
        monthly_rent, tenancy_months
    )
    rent_limit_pass = advance <= maximum_advance

    applicant_type = str(
        get_state_val(
            ["saved_applicant_type", "input_applicant_type", "applicant_type"],
            "Salaried / Employed",
        )
    ).lower()

    # Explicit match prevents "Self-Employed" from matching "Employed"
    is_salaried = "business" not in applicant_type and "self-employed" not in applicant_type

    # Credit history parsing
    raw_credit = str(
        get_state_val(
            ["saved_credit_history", "input_credit_history", "credit_history"], ""
        )
    ).lower()

    if "clean" in raw_credit or "satisfactory" in raw_credit:
        credit_points = 0.0
        credit_label = "Clean / Satisfactory"
    elif "adverse" in raw_credit or "delinquent" in raw_credit or "bad" in raw_credit:
        credit_points = 2.0
        credit_label = "Adverse / Delinquencies"
    else:
        credit_points = 1.0
        credit_label = "Limited / No formal credit history"

    # --- 3. Salaried Affordability & Scoring ---
    if is_salaried:
        if salary > 0:
            dsr = (total_monthly_debt / salary) * 100.0
        else:
            dsr = 0.0

        affordability = "PASS" if (salary > 0 and dsr <= DSR_THRESHOLD) else "FAIL"

        # Employment type parsing
        raw_emp = str(
            get_state_val(
                ["saved_employment_type", "input_employment_type", "employment_type"],
                "",
            )
        ).lower()

        is_government = "gov" in raw_emp or "civil" in raw_emp or "public" in raw_emp
        emp_type_label = (
            "Government Institution" if is_government else "Private / Corporate"
        )
        emp_points = 0.0 if is_government else 1.0

        # Job tenure parsing
        raw_years = str(
            get_state_val(
                ["saved_years_at_job", "input_years_at_job", "years_at_job"], ""
            )
        ).lower()

        if "2" in raw_years or "3" in raw_years or "more" in raw_years:
            tenure_points = 0.0 if is_government else 0.5
            tenure_label = "2+ years"
        elif "1" in raw_years or "one" in raw_years:
            tenure_points = 0.0 if is_government else 1.0
            tenure_label = "1 year"
        elif "6" in raw_years:
            tenure_points = 1.0 if is_government else 2.0
            tenure_label = "6 months to 1 year"
        else:
            tenure_points = 2.0 if is_government else 3.0
            tenure_label = "< 6 months (Probation)"

        risk_score = emp_points + tenure_points + credit_points

        risk_reasons = [
            f"Employment type: {emp_type_label} ({emp_points:g} pts)",
            f"Tenure at job: {tenure_label} ({tenure_points:g} pts)",
            f"Credit history: {credit_label} ({credit_points:g} pts)",
        ]

        risk_rationale = (
            "Assessment weighted primarily on government employment security, tenure, and credit history."
            if is_government
            else "Assessment weighted on private sector job stability, probation status, and credit history."
        )

        business_affordability = None

    # --- 4. Unsalaried / Business Profile ---
    else:
        business_profit = float(
            get_state_val(
                ["saved_business_profit", "input_business_profit", "business_profit"],
                0.0,
            )
        )
        cash_flow = float(
            get_state_val(
                [
                    "saved_business_cash_flow",
                    "input_business_cash_flow",
                    "business_cash_flow",
                ],
                0.0,
            )
        )

        business_affordability = (
            business_profit > 0 and cash_flow > 0 and cash_flow >= monthly_repayment
        )
        affordability = "PASS" if business_affordability else "FAIL"

        cash_flow_points = 0.0 if cash_flow >= monthly_repayment else 2.0
        profit_points = 0.0 if business_profit > 0 else 2.0

        guarantor_avail = str(
            get_state_val(["guarantor_available", "input_guarantor_available"], "")
        ).lower()
        guarantor_cred = str(
            get_state_val(["guarantor_credit", "input_guarantor_credit"], "")
        ).lower()
        has_guarantor = "yes" in guarantor_avail and (
            "clean" in guarantor_cred or "satisfactory" in guarantor_cred
        )
        guarantor_points = -1.0 if has_guarantor else 1.0

        risk_score = (
            cash_flow_points + profit_points + credit_points + guarantor_points
        )

        risk_reasons = [
            f"Cash flow coverage: {money(cash_flow)} ({cash_flow_points:g} pts)",
            f"Business profit: {money(business_profit)} ({profit_points:g} pts)",
            f"Credit character: {credit_label} ({credit_points:g} pts)",
            f"Guarantor status: {'Verified Clean' if has_guarantor else 'None / Unverified'} ({guarantor_points:g} pts)",
        ]

        risk_rationale = (
            "Assessment weighted on cash flow coverage, net profit, and guarantor backing."
        )
        dsr = None

    # Risk Tier assignment
    if risk_score <= 1.5:
        repayment_risk = "LOW"
    elif risk_score <= 3.0:
        repayment_risk = "MEDIUM"
    else:
        repayment_risk = "HIGH"

    conditional_offer = (
        rent_limit_pass
        and affordability == "PASS"
        and repayment_risk in ["LOW", "MEDIUM"]
    )

    return {
        "monthly_repayment": monthly_repayment,
        "existing_debt": existing_debt,
        "total_monthly_debt": total_monthly_debt,
        "dsr": dsr,
        "repayment_period": repayment_period,
        "rent_limit_pass": rent_limit_pass,
        "allowed_months": allowed_months,
        "maximum_advance": maximum_advance,
        "affordability": affordability,
        "repayment_risk": repayment_risk,
        "risk_reasons": risk_reasons,
        "risk_rationale": risk_rationale,
        "conditional_offer": conditional_offer,
        "thin_credit": credit_points == 1.0,
        "business_affordability": business_affordability,
        "salary": salary,
        "risk_score": risk_score,
        "is_salaried": is_salaried,
    }











#code works well only that for unsalaried applicant on the underwriting page its showing repayment risk values for salaried
# """Underwriting calculations and decision logic with robust session state fallbacks."""

# import streamlit as st
# from config import DSR_THRESHOLD
# from utils.helpers import calculate_rent_advance_limit, money, parse_tenancy_months


# def get_state_val(keys, default):
#     """Safely retrieves the first non-None, non-empty value across multiple session state key aliases."""
#     for key in keys:
#         if key in st.session_state:
#             val = st.session_state[key]
#             if val is not None and val != "":
#                 return val
#     return default


# def calculate_assessment():
#     """Calculates risk, affordability, and loan terms using multi-key session state retrieval."""

#     # --- 1. Retrieve Financial Inputs Safely Across Widget Aliases ---
#     monthly_rent = float(
#         get_state_val(["saved_monthly_rent", "input_monthly_rent", "monthly_rent"], 0.0)
#     )

#     advance = float(
#         get_state_val(["saved_advance_amount", "input_advance_amount", "advance_amount"], 0.0)
#     )

#     tenancy_duration = get_state_val(
#         ["saved_tenancy_duration", "input_tenancy_duration", "tenancy_duration"], "12 months"
#     )

#     repayment_period = max(
#         int(
#             get_state_val(
#                 ["saved_repayment_period", "input_repayment_period", "repayment_period"],
#                 12,
#             )
#         ),
#         1,
#     )

#     salary = float(
#         get_state_val(["saved_salary", "input_salary", "salary"], 0.0)
#     )

#     existing_debt = float(
#         get_state_val(["saved_existing_debt", "input_existing_debt", "existing_debt"], 0.0)
#     )

#     # Calculate monthly installments & total commitment
#     monthly_repayment = advance / repayment_period if repayment_period > 0 else advance
#     total_monthly_debt = existing_debt + monthly_repayment

#     # --- 2. Calculate Rent-Advance Eligibility Cap ---
#     tenancy_months = parse_tenancy_months(tenancy_duration) if tenancy_duration else 0
#     allowed_months, maximum_advance = calculate_rent_advance_limit(
#         monthly_rent, tenancy_months
#     )
#     rent_limit_pass = advance <= maximum_advance

#     applicant_type = str(
#         get_state_val(
#             ["saved_applicant_type", "input_applicant_type", "applicant_type"],
#             "Salaried / Employed",
#         )
#     ).lower()
#     is_salaried = "salaried" in applicant_type or "employed" in applicant_type

#     # Credit history parsing
#     raw_credit = str(
#         get_state_val(
#             ["saved_credit_history", "input_credit_history", "credit_history"], ""
#         )
#     ).lower()

#     if "clean" in raw_credit or "satisfactory" in raw_credit:
#         credit_points = 0.0
#         credit_label = "Clean / Satisfactory"
#     elif "adverse" in raw_credit or "delinquent" in raw_credit or "bad" in raw_credit:
#         credit_points = 2.0
#         credit_label = "Adverse / Delinquencies"
#     else:
#         credit_points = 1.0
#         credit_label = "Limited / No formal credit history"

#     # --- 3. Salaried Affordability & Scoring ---
#     if is_salaried:
#         if salary > 0:
#             dsr = (total_monthly_debt / salary) * 100.0
#         else:
#             dsr = 0.0

#         affordability = "PASS" if (salary > 0 and dsr <= DSR_THRESHOLD) else "FAIL"

#         # Employment type parsing
#         raw_emp = str(
#             get_state_val(
#                 ["saved_employment_type", "input_employment_type", "employment_type"],
#                 "",
#             )
#         ).lower()

#         is_government = "gov" in raw_emp or "civil" in raw_emp or "public" in raw_emp
#         emp_type_label = (
#             "Government Institution" if is_government else "Private / Corporate"
#         )
#         emp_points = 0.0 if is_government else 1.0

#         # Job tenure parsing
#         raw_years = str(
#             get_state_val(
#                 ["saved_years_at_job", "input_years_at_job", "years_at_job"], ""
#             )
#         ).lower()

#         if "2" in raw_years or "3" in raw_years or "more" in raw_years:
#             tenure_points = 0.0 if is_government else 0.5
#             tenure_label = "2+ years"
#         elif "1" in raw_years or "one" in raw_years:
#             tenure_points = 0.0 if is_government else 1.0
#             tenure_label = "1 year"
#         elif "6" in raw_years:
#             tenure_points = 1.0 if is_government else 2.0
#             tenure_label = "6 months to 1 year"
#         else:
#             tenure_points = 2.0 if is_government else 3.0
#             tenure_label = "< 6 months (Probation)"

#         risk_score = emp_points + tenure_points + credit_points

#         risk_reasons = [
#             f"Employment type: {emp_type_label} ({emp_points:g} pts)",
#             f"Tenure at job: {tenure_label} ({tenure_points:g} pts)",
#             f"Credit history: {credit_label} ({credit_points:g} pts)",
#         ]

#         risk_rationale = (
#             "Assessment weighted primarily on government employment security, tenure, and credit history."
#             if is_government
#             else "Assessment weighted on private sector job stability, probation status, and credit history."
#         )

#         business_affordability = None

#     # --- 4. Unsalaried / Business Profile ---
#     else:
#         business_profit = float(
#             get_state_val(
#                 ["saved_business_profit", "input_business_profit", "business_profit"],
#                 0.0,
#             )
#         )
#         cash_flow = float(
#             get_state_val(
#                 [
#                     "saved_business_cash_flow",
#                     "input_business_cash_flow",
#                     "business_cash_flow",
#                 ],
#                 0.0,
#             )
#         )

#         business_affordability = (
#             business_profit > 0 and cash_flow > 0 and cash_flow >= monthly_repayment
#         )
#         affordability = "PASS" if business_affordability else "FAIL"

#         cash_flow_points = 0.0 if cash_flow >= monthly_repayment else 2.0
#         profit_points = 0.0 if business_profit > 0 else 2.0

#         guarantor_avail = str(
#             get_state_val(["guarantor_available", "input_guarantor_available"], "")
#         ).lower()
#         guarantor_cred = str(
#             get_state_val(["guarantor_credit", "input_guarantor_credit"], "")
#         ).lower()
#         has_guarantor = "yes" in guarantor_avail and (
#             "clean" in guarantor_cred or "satisfactory" in guarantor_cred
#         )
#         guarantor_points = -1.0 if has_guarantor else 1.0

#         risk_score = (
#             cash_flow_points + profit_points + credit_points + guarantor_points
#         )

#         risk_reasons = [
#             f"Cash flow coverage: {money(cash_flow)} ({cash_flow_points:g} pts)",
#             f"Business profit: {money(business_profit)} ({profit_points:g} pts)",
#             f"Credit character: {credit_label} ({credit_points:g} pts)",
#             f"Guarantor status: {'Verified Clean' if has_guarantor else 'None / Unverified'} ({guarantor_points:g} pts)",
#         ]

#         risk_rationale = (
#             "Assessment weighted on cash flow coverage, net profit, and guarantor backing."
#         )
#         dsr = None

#     # Risk Tier assignment
#     if risk_score <= 1.5:
#         repayment_risk = "LOW"
#     elif risk_score <= 3.0:
#         repayment_risk = "MEDIUM"
#     else:
#         repayment_risk = "HIGH"

#     conditional_offer = (
#         rent_limit_pass
#         and affordability == "PASS"
#         and repayment_risk in ["LOW", "MEDIUM"]
#     )

#     return {
#         "monthly_repayment": monthly_repayment,
#         "existing_debt": existing_debt,
#         "total_monthly_debt": total_monthly_debt,
#         "dsr": dsr,
#         "repayment_period": repayment_period,
#         "rent_limit_pass": rent_limit_pass,
#         "allowed_months": allowed_months,
#         "maximum_advance": maximum_advance,
#         "affordability": affordability,
#         "repayment_risk": repayment_risk,
#         "risk_reasons": risk_reasons,
#         "risk_rationale": risk_rationale,
#         "conditional_offer": conditional_offer,
#         "thin_credit": credit_points == 1.0,
#         "business_affordability": business_affordability,
#         "salary": salary,
#         "risk_score": risk_score,
#         "is_salaried": is_salaried,
#     }












# working code but was giving issues with display under explanation tabs in verification and offer page, especially under affordability tab
# """Underwriting calculations and decision logic with robust session state fallbacks."""

# import streamlit as st
# from config import DSR_THRESHOLD
# from utils.helpers import calculate_rent_advance_limit, money, parse_tenancy_months


# def calculate_assessment():
#     """Calculates risk, affordability, and loan terms using safe state retrieval."""

#     # --- 1. Retrieve Financial Inputs (Fallback Checks) ---
#     monthly_rent = float(
#         st.session_state.get("saved_monthly_rent")
#         or st.session_state.get("monthly_rent")
#         or 0.0
#     )

#     advance = float(
#         st.session_state.get("saved_advance_amount")
#         or st.session_state.get("advance_amount")
#         or 0.0
#     )

#     tenancy_duration = st.session_state.get(
#         "saved_tenancy_duration"
#     ) or st.session_state.get("tenancy_duration")

#     repayment_period = max(
#         int(
#             st.session_state.get("saved_repayment_period")
#             or st.session_state.get("repayment_period")
#             or 12
#         ),
#         1,
#     )

#     salary = float(
#         st.session_state.get("saved_salary")
#         or st.session_state.get("salary")
#         or 0.0
#     )

#     existing_debt = float(
#         st.session_state.get("saved_existing_debt")
#         or st.session_state.get("existing_debt")
#         or 0.0
#     )

#     # Calculate installments accurately
#     monthly_repayment = advance / repayment_period if repayment_period > 0 else advance
#     total_monthly_debt = existing_debt + monthly_repayment

#     # --- 2. Calculate Rent-Advance Eligibility Cap ---
#     tenancy_months = parse_tenancy_months(tenancy_duration) if tenancy_duration else 0
#     allowed_months, maximum_advance = calculate_rent_advance_limit(
#         monthly_rent, tenancy_months
#     )
#     rent_limit_pass = advance <= maximum_advance

#     applicant_type = str(
#         st.session_state.get("applicant_type") or "Salaried / Employed"
#     ).lower()
#     is_salaried = "salaried" in applicant_type or "employed" in applicant_type

#     # Credit history parsing
#     raw_credit = str(
#         st.session_state.get("saved_credit_history")
#         or st.session_state.get("credit_history")
#         or ""
#     ).lower()
#     if "clean" in raw_credit or "satisfactory" in raw_credit:
#         credit_points = 0.0
#         credit_label = "Clean / Satisfactory"
#     elif "adverse" in raw_credit or "delinquent" in raw_credit or "bad" in raw_credit:
#         credit_points = 2.0
#         credit_label = "Adverse / Delinquencies"
#     else:
#         credit_points = 1.0
#         credit_label = "Limited / No formal credit history"

#     # --- 3. Salaried Affordability & Scoring ---
#     if is_salaried:
#         if salary > 0:
#             dsr = (total_monthly_debt / salary) * 100.0
#         else:
#             dsr = 0.0

#         affordability = "PASS" if (salary > 0 and dsr <= DSR_THRESHOLD) else "FAIL"

#         # Employment type parsing
#         raw_emp = str(
#             st.session_state.get("saved_employment_type")
#             or st.session_state.get("employment_type")
#             or ""
#         ).lower()
#         is_government = "gov" in raw_emp or "civil" in raw_emp or "public" in raw_emp
#         emp_type_label = "Government Institution" if is_government else "Private / Corporate"
#         emp_points = 0.0 if is_government else 1.0

#         # Job tenure parsing
#         raw_years = str(
#             st.session_state.get("saved_years_at_job")
#             or st.session_state.get("years_at_job")
#             or ""
#         ).lower()
#         if "2" in raw_years or "3" in raw_years or "more" in raw_years:
#             tenure_points = 0.0 if is_government else 0.5
#             tenure_label = "2+ years"
#         elif "1" in raw_years:
#             tenure_points = 0.0 if is_government else 1.0
#             tenure_label = "1 year"
#         elif "6" in raw_years:
#             tenure_points = 1.0 if is_government else 2.0
#             tenure_label = "6 months to 1 year"
#         else:
#             tenure_points = 2.0 if is_government else 3.0
#             tenure_label = "< 6 months (Probation)"

#         risk_score = emp_points + tenure_points + credit_points

#         risk_reasons = [
#             f"Employment type: {emp_type_label} ({emp_points:g} pts)",
#             f"Tenure at job: {tenure_label} ({tenure_points:g} pts)",
#             f"Credit history: {credit_label} ({credit_points:g} pts)",
#         ]

#         risk_rationale = (
#             "Assessment weighted primarily on government employment security, tenure, and credit history."
#             if is_government
#             else "Assessment weighted on private sector job stability, probation status, and credit history."
#         )

#         business_affordability = None

#     # --- 4. Unsalaried / Business Profile ---
#     else:
#         business_profit = float(
#             st.session_state.get("saved_business_profit")
#             or st.session_state.get("business_profit")
#             or 0.0
#         )
#         cash_flow = float(
#             st.session_state.get("saved_business_cash_flow")
#             or st.session_state.get("business_cash_flow")
#             or 0.0
#         )

#         business_affordability = (
#             business_profit > 0 and cash_flow > 0 and cash_flow >= monthly_repayment
#         )
#         affordability = "PASS" if business_affordability else "FAIL"

#         cash_flow_points = 0.0 if cash_flow >= monthly_repayment else 2.0
#         profit_points = 0.0 if business_profit > 0 else 2.0

#         guarantor_avail = str(st.session_state.get("guarantor_available") or "").lower()
#         guarantor_cred = str(st.session_state.get("guarantor_credit") or "").lower()
#         has_guarantor = "yes" in guarantor_avail and (
#             "clean" in guarantor_cred or "satisfactory" in guarantor_cred
#         )
#         guarantor_points = -1.0 if has_guarantor else 1.0

#         risk_score = cash_flow_points + profit_points + credit_points + guarantor_points

#         risk_reasons = [
#             f"Cash flow coverage: {money(cash_flow)} ({cash_flow_points:g} pts)",
#             f"Business profit: {money(business_profit)} ({profit_points:g} pts)",
#             f"Credit character: {credit_label} ({credit_points:g} pts)",
#             f"Guarantor status: {'Verified Clean' if has_guarantor else 'None / Unverified'} ({guarantor_points:g} pts)",
#         ]

#         risk_rationale = "Assessment weighted on cash flow coverage, net profit, and guarantor backing."
#         dsr = None

#     # Risk Tier assignment
#     if risk_score <= 1.5:
#         repayment_risk = "LOW"
#     elif risk_score <= 3.0:
#         repayment_risk = "MEDIUM"
#     else:
#         repayment_risk = "HIGH"

#     conditional_offer = (
#         rent_limit_pass
#         and affordability == "PASS"
#         and repayment_risk in ["LOW", "MEDIUM"]
#     )

#     return {
#         "monthly_repayment": monthly_repayment,
#         "existing_debt": existing_debt,
#         "total_monthly_debt": total_monthly_debt,
#         "dsr": dsr,
#         "repayment_period": repayment_period,
#         "rent_limit_pass": rent_limit_pass,
#         "allowed_months": allowed_months,
#         "maximum_advance": maximum_advance,
#         "affordability": affordability,
#         "repayment_risk": repayment_risk,
#         "risk_reasons": risk_reasons,
#         "risk_rationale": risk_rationale,
#         "conditional_offer": conditional_offer,
#         "thin_credit": credit_points == 1.0,
#         "business_affordability": business_affordability,
#         "salary": salary,
#         "risk_score": risk_score,
#         "is_salaried": is_salaried,
#     }








# """Underwriting calculations and decision logic with robust state handling."""

# import streamlit as st
# from config import DSR_THRESHOLD
# from utils.helpers import calculate_rent_advance_limit, money, parse_tenancy_months


# def calculate_assessment():
#     """Calculates risk, affordability, and loan terms using fallback state checks."""

#     # --- 1. Safely retrieve inputs with fallbacks ---
#     monthly_rent = float(
#         st.session_state.get("saved_monthly_rent")
#         or st.session_state.get("monthly_rent")
#         or 0.0
#     )

#     advance = float(
#         st.session_state.get("saved_advance_amount")
#         or st.session_state.get("advance_amount")
#         or 0.0
#     )

#     tenancy_duration = st.session_state.get(
#         "saved_tenancy_duration"
#     ) or st.session_state.get("tenancy_duration")

#     # Ensure repayment_period defaults to at least 1, checking saved alias first
#     period = max(
#         int(
#             st.session_state.get("saved_repayment_period")
#             or st.session_state.get("repayment_period")
#             or 1
#         ),
#         1,
#     )

#     monthly_repayment = advance / period

#     # Safely retrieve existing debt & salary with fallbacks
#     existing_debt = float(
#         st.session_state.get("saved_existing_debt")
#         or st.session_state.get("existing_debt")
#         or 0.0
#     )
#     total_monthly_debt = existing_debt + monthly_repayment

#     # --- 2. Rent-Advance Limit ---
#     tenancy_months = (
#         parse_tenancy_months(tenancy_duration) if tenancy_duration else 0
#     )
#     allowed_months, maximum_advance = calculate_rent_advance_limit(
#         monthly_rent,
#         tenancy_months,
#     )
#     rent_limit_pass = advance <= maximum_advance

#     applicant_type = str(
#         st.session_state.get("applicant_type") or "Salaried / Employed"
#     ).lower()
#     is_salaried = "salaried" in applicant_type or "employed" in applicant_type

#     # Safe credit history parser
#     raw_credit = str(st.session_state.get("credit_history") or "").lower()
#     if "clean" in raw_credit or "satisfactory" in raw_credit:
#         credit_points = 0.0
#         credit_label = "Clean / Satisfactory"
#     elif "adverse" in raw_credit or "delinquent" in raw_credit or "bad" in raw_credit:
#         credit_points = 2.0
#         credit_label = "Adverse / Delinquencies"
#     else:
#         credit_points = 1.0
#         credit_label = "Limited / No formal credit history"

#     # --- 3. Salaried Profile ---
#     if is_salaried:
#         salary = float(
#             st.session_state.get("saved_salary")
#             or st.session_state.get("salary")
#             or 0.0
#         )

#         if salary > 0:
#             dsr = (total_monthly_debt / salary) * 100.0
#         else:
#             dsr = None

#         affordability = (
#             "PASS" if (dsr is not None and dsr <= DSR_THRESHOLD) else "FAIL"
#         )

#         # Employment type check
#         raw_emp = str(st.session_state.get("employment_type") or "").lower()
#         is_government = (
#             "gov" in raw_emp or "civil" in raw_emp or "public" in raw_emp
#         )
#         emp_type_label = (
#             "Government Institution" if is_government else "Private / Corporate"
#         )
#         emp_points = 0.0 if is_government else 1.0

#         # Tenure check
#         raw_years = str(st.session_state.get("years_at_job") or "").lower()
#         if "2" in raw_years or "3" in raw_years or "more" in raw_years:
#             tenure_points = 0.0 if is_government else 0.5
#             tenure_label = "2+ years"
#         elif "1" in raw_years:
#             tenure_points = 0.0 if is_government else 1.0
#             tenure_label = "1 year"
#         elif "6" in raw_years:
#             tenure_points = 1.0 if is_government else 2.0
#             tenure_label = "6 months to 1 year"
#         else:
#             tenure_points = 2.0 if is_government else 3.0
#             tenure_label = "< 6 months (Probation)"

#         risk_score = emp_points + tenure_points + credit_points

#         risk_reasons = [
#             f"Employment type: {emp_type_label} ({emp_points:g} pts)",
#             f"Tenure at job: {tenure_label} ({tenure_points:g} pts)",
#             f"Credit history: {credit_label} ({credit_points:g} pts)",
#         ]

#         risk_rationale = (
#             "Assessment weighted primarily on government employment security, job tenure, "
#             "and credit history."
#             if is_government
#             else "Assessment weighted on private sector job stability, probation status, "
#             "and credit history."
#         )

#         business_affordability = None

#     # --- 4. Unsalaried / Business Profile ---
#     else:
#         business_profit = float(
#             st.session_state.get("saved_business_profit")
#             or st.session_state.get("business_profit")
#             or 0.0
#         )
#         cash_flow = float(
#             st.session_state.get("saved_business_cash_flow")
#             or st.session_state.get("business_cash_flow")
#             or 0.0
#         )

#         business_affordability = (
#             business_profit > 0
#             and cash_flow > 0
#             and cash_flow >= monthly_repayment
#         )
#         affordability = "PASS" if business_affordability else "FAIL"

#         cash_flow_points = 0.0 if cash_flow >= monthly_repayment else 2.0
#         profit_points = 0.0 if business_profit > 0 else 2.0

#         guarantor_avail = str(
#             st.session_state.get("guarantor_available") or ""
#         ).lower()
#         guarantor_cred = str(
#             st.session_state.get("guarantor_credit") or ""
#         ).lower()
#         has_guarantor = "yes" in guarantor_avail and (
#             "clean" in guarantor_cred or "satisfactory" in guarantor_cred
#         )
#         guarantor_points = -1.0 if has_guarantor else 1.0

#         risk_score = (
#             cash_flow_points + profit_points + credit_points + guarantor_points
#         )

#         risk_reasons = [
#             f"Cash flow coverage: {money(cash_flow)} ({cash_flow_points:g} pts)",
#             f"Business profit: {money(business_profit)} ({profit_points:g} pts)",
#             f"Credit character: {credit_label} ({credit_points:g} pts)",
#             f"Guarantor status: {'Verified Clean' if has_guarantor else 'None / Unverified'} ({guarantor_points:g} pts)",
#         ]

#         risk_rationale = "Assessment weighted on cash flow coverage, net profit, and guarantor backing."
#         dsr = None
#         salary = None

#     # Risk Tiers
#     if risk_score <= 1.5:
#         repayment_risk = "LOW"
#     elif risk_score <= 3.0:
#         repayment_risk = "MEDIUM"
#     else:
#         repayment_risk = "HIGH"

#     conditional_offer = (
#         rent_limit_pass
#         and affordability == "PASS"
#         and repayment_risk in ["LOW", "MEDIUM"]
#     )

#     return {
#         "monthly_repayment": monthly_repayment,
#         "existing_debt": existing_debt,
#         "total_monthly_debt": total_monthly_debt,
#         "dsr": dsr,
#         "repayment_period": period,
#         "rent_limit_pass": rent_limit_pass,
#         "allowed_months": allowed_months,
#         "maximum_advance": maximum_advance,
#         "affordability": affordability,
#         "repayment_risk": repayment_risk,
#         "risk_reasons": risk_reasons,
#         "risk_rationale": risk_rationale,
#         "conditional_offer": conditional_offer,
#         "thin_credit": credit_points == 1.0,
#         "business_affordability": business_affordability,
#         "salary": salary,
#         "risk_score": risk_score,
#         "is_salaried": is_salaried,
#     }