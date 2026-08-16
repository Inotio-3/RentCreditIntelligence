RENTREADY MODULAR MVP

Folder structure:

app.py                         Main Streamlit entry point
config.py                      POC assumptions + default session fields
logic/underwriting.py          Underwriting calculations and demo rules
screens/profile.py             Profile selection
screens/applicant_rent.py     Applicant & rent inputs
screens/financials.py          Financial inputs + document uploads
screens/underwriting.py        Affordability + repayment-risk display
screens/decision.py            Verification + conditional offer display
utils/state.py                 Session-state setup/reset
utils/helpers.py               Formatting + rental-rule helpers
utils/ui.py                    CSS, header and progress bar

RUN:
1. Keep this folder structure intact.
2. Open a terminal in the rentready_mvp_modular folder.
3. Run: streamlit run app.py

The current demo logic is intentionally simple. The main place to edit underwriting calculations/rules is:
logic/underwriting.py
