"""Small reusable formatting and rental-rule helpers."""

import streamlit as st

def money(value):
    """Format a number as Ghana cedis."""
    try:
        return f"GHS {value:,.0f}"
    except (TypeError, ValueError):
        return "GHS 0"

def parse_tenancy_months(value):
    """Convert the visible tenancy choice into a number of months."""
    return int(value.split()[0])

def calculate_rent_advance_limit(monthly_rent, tenancy_months):
    """POC rental-rule calculation, kept separate from credit risk."""
    if tenancy_months > 6:
        months_allowed = 6
    else:
        months_allowed = 2
    maximum_advance = monthly_rent * months_allowed
    return months_allowed, maximum_advance

def get_step_state(step):
    current = st.session_state.step
    if step < current:
        return "complete"
    if step == current:
        return "active"
    return "future"

def badge(text, kind="neutral"):
    return f'<span class="badge {kind}">{text}</span>'

def verification_status(uploaded_file):
    return "Uploaded — Verification pending" if uploaded_file else "Not uploaded"
