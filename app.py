import streamlit as st

from utils.state import init_session_state
from utils.ui import load_css, render_header
from screens.profile import screen_profile
from screens.applicant_rent import screen_rent
from screens.financials import screen_financials
from screens.underwriting import screen_underwriting
from screens.decision import screen_decision


st.set_page_config(
    page_title="RentAsess | Underwriting Portal",
    page_icon="🔑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 1. Initialize session state safely
init_session_state()

# 2. Ensure active step exists
if "step" not in st.session_state:
    st.session_state.step = 0

load_css()
render_header()

# 3. Router logic
if st.session_state.step == 0:
    screen_profile()
elif st.session_state.step == 1:
    screen_rent()
elif st.session_state.step == 2:
    screen_financials()
elif st.session_state.step == 3:
    screen_underwriting()
elif st.session_state.step == 4:
    screen_decision()
else:
    st.session_state.step = 0
    st.rerun()









#works perfectly no issues
# import streamlit as st

# from utils.state import init_session_state
# from utils.ui import load_css, render_header
# from screens.profile import screen_profile
# from screens.applicant_rent import screen_rent
# from screens.financials import screen_financials
# from screens.underwriting import screen_underwriting
# from screens.decision import screen_decision


# st.set_page_config(
#     page_title="RentAsess | Underwriting Portal",
#     page_icon="🔑",
#     layout="wide",
#     initial_sidebar_state="collapsed",
# )

# init_session_state()
# load_css()
# render_header()

# if st.session_state.step == 0:
#     screen_profile()
# elif st.session_state.step == 1:
#     screen_rent()
# elif st.session_state.step == 2:
#     screen_financials()
# elif st.session_state.step == 3:
#     screen_underwriting()
# elif st.session_state.step == 4:
#     screen_decision()
# else:
#     st.session_state.step = 0
#     st.rerun()
