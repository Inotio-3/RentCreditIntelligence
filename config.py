"""Configurable POC assumptions and shared application defaults."""

DSR_THRESHOLD = 40.0                 # DEMO ASSUMPTION
DEMO_REPAYMENT_PERIOD = 3             # DEMO ASSUMPTION
DEMO_INTEREST_RATE = 0.0              # POC: no interest/fees included

DEFAULTS = {
    "step": 0,
    "applicant_type": None,
    "young_graduate": False,
    "monthly_rent": None,
    "tenancy_duration": None,
    "advance_amount": None,
    "purpose": None,
    "salary": None,
    "existing_debt": None,
    "employment_type": None,
    "years_at_job": None,
    "credit_history": None,
    "business_income": None,
    "business_profit": None,
    "business_cash_flow": None,
    "guarantor_available": None,
    "guarantor_credit": None,
    "repayment_period": None,
    "rent_limit_pass": None,
    "affordability_result": "PENDING",
    "repayment_risk": "PENDING",
    "conditional_offer": False,
    "assessment_run": False,
    "verification_run": False,
    "payslip": None,
    "employment_proof": None,
    "rental_proof": None,
    "business_proof": None,
    "guarantor_proof": None,
}
