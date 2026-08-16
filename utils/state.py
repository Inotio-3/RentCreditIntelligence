"""Session-state setup for the RentReady POC."""

import streamlit as st
from config import DEFAULTS

# Baseline fallback defaults to guarantee stability across screen navigation
FALLBACK_DEFAULTS = {
    "step": 1,
    "applicant_type": "Salaried / Employed",
    "monthly_rent": 0.0,
    "advance_amount": 0.0,
    "tenancy_duration": None,
    "repayment_period": 12,
    "existing_debt": 0.0,
    "salary": 0.0,
    "employment_type": "Private / Corporate",
    "years_at_job": "< 1 year",
    "credit_history": "No formal credit history",
    "business_income": 0.0,
    "business_profit": 0.0,
    "business_cash_flow": 0.0,
    "guarantor_available": "No",
    "guarantor_credit": "Unknown / not verified",
    # Safe saved-state fallback keys
    "saved_monthly_rent": None,
    "saved_advance_amount": None,
    "saved_tenancy_duration": None,
    "verification_run": False,
}


def _get_combined_defaults():
    """Combines hardcoded baseline fallbacks with configuration DEFAULTS."""
    combined = FALLBACK_DEFAULTS.copy()
    if isinstance(DEFAULTS, dict):
        combined.update(DEFAULTS)
    return combined


def init_session_state():
    """Initializes session state keys if they do not already exist."""
    defaults = _get_combined_defaults()
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session_state():
    """Resets all tracked keys back to their default values."""
    defaults = _get_combined_defaults()
    for key, value in defaults.items():
        st.session_state[key] = value




# """Session-state setup for the RentReady POC."""

# import streamlit as st
# from config import DEFAULTS

# def init_session_state():
#     for key, value in DEFAULTS.items():
#         if key not in st.session_state:
#             st.session_state[key] = value

# def reset_session_state():
#     for key, value in DEFAULTS.items():
#         st.session_state[key] = value
