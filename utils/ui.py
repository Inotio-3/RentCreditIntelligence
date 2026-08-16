"""Shared visual components."""

import streamlit as st
from utils.helpers import get_step_state


def load_css():
    st.markdown(
    """
<style>
    /* ---------- Global ---------- */
    .stApp {
        background: #f7f9fb;
        color: #162033;
    }

    [data-testid="stAppViewContainer"] > .main {
        padding-top: 0rem;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 0.5rem;
        padding-bottom: 2rem;
    }

    /* Hide Streamlit chrome for a cleaner POC */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ---------- Header ---------- */
    .topbar {
        height: 58px;
        margin: -0.5rem -3rem 1.5rem -3rem;
        padding: 0 2rem;
        background: white;
        border-bottom: 1px solid #e1e7ee;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .brand-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .brand-icon {
        width: 30px;
        height: 30px;
        border-radius: 7px;
        background: #006b57;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        font-weight: 700;
    }

    .brand-icon svg {
    width: 18px;
    height: 18px;
    fill: none;
    stroke: currentColor;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
    }

    .brand {
        color: #006b57;
        font-weight: 750;
        font-size: 16px;
    }

    .brand-divider {
        height: 20px;
        width: 1px;
        background: #d9e0e8;
        margin: 0 2px;
    }

    .portal {
        color: #56657b;
        font-size: 12px;
    }

    .user {
        text-align: right;
        font-size: 11px;
        color: #162033;
        line-height: 1.2;
    }

    .user small {
        color: #8b98a9;
        font-size: 9px;
    }

    /* ---------- Headings ---------- */
    .page-title {
        text-align: center;
        font-size: 28px;
        font-weight: 760;
        color: #162033;
        margin: 3rem 0 0.35rem 0;
    }

    .page-subtitle {
        text-align: center;
        color: #66758a;
        font-size: 13px;
        line-height: 1.5;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 15px;
        font-weight: 700;
        color: #162033;
        margin-bottom: 0.8rem;
    }

    /* ---------- Cards ---------- */
    .card {
        background: white;
        border: 1px solid #dfe6ee;
        border-radius: 12px;
        padding: 1.35rem;
        box-shadow: 0 1px 2px rgba(20, 35, 55, 0.02);
        margin-bottom: 1rem;
    }

    .soft-card {
        background: #f7f9fb;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #edf1f5;
    }

    .green-card {
        background: #e8f5f1;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #d6eee6;
    }

    .metric-label {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: .04em;
        color: #547266;
        font-weight: 700;
    }

    .metric-value {
        font-size: 21px;
        font-weight: 760;
        color: #006b57;
        margin-top: 5px;
    }

    .small-note {
        color: #8190a2;
        font-size: 10px;
        line-height: 1.5;
    }

    .rule-note {
        color: #7f8d9e;
        font-size: 10px;
        line-height: 1.45;
        margin-top: 0.7rem;
    }

    /* ---------- Profile cards ---------- */
    .profile-card {
        background: white;
        border: 1px solid #dfe6ee;
        border-radius: 12px;
        padding: 1.3rem;
        min-height: 155px;
    }

    .profile-card.selected {
        border: 2px solid #006b57;
    }

    .profile-icon {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #edf4f1;
        color: #006b57;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.7rem;
    }

    .profile-icon svg {
    width: 22px;
    height: 22px;
    fill: none;
    stroke: currentColor;
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
    }

    .profile-name {
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }

    .profile-description {
        font-size: 10px;
        color: #65748a;
        line-height: 1.55;
    }

    /* ---------- Progress ---------- */
    .progress-wrap {
        background: transparent;
        margin: 0.2rem 0 1.5rem 0;
    }

    .progress-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0;
    }

    .progress-item {
        position: relative;
        color: #91a0b2;
        font-size: 10px;
        padding-bottom: 12px;
        border-bottom: 3px solid #e2e8ef;
    }

    .progress-item.active,
    .progress-item.complete {
        color: #006b57;
        border-bottom-color: #006b57;
        font-weight: 700;
    }

    .progress-number {
        display: inline-flex;
        width: 19px;
        height: 19px;
        border-radius: 50%;
        align-items: center;
        justify-content: center;
        background: #e7edf4;
        color: #7d8ca0;
        margin-right: 6px;
        font-size: 9px;
    }

    .progress-item.active .progress-number,
    .progress-item.complete .progress-number {
        background: #006b57;
        color: white;
    }

    /* ---------- Result cards ---------- */
    .result-card {
        background: white;
        border: 1px solid #dfe6ee;
        border-radius: 12px;
        padding: 1.25rem;
        min-height: 145px;
    }

    .result-title {
        font-size: 14px;
        font-weight: 700;
        color: #162033;
    }

    .result-value {
        font-size: 20px;
        font-weight: 760;
        margin-top: 0.5rem;
    }

    .pass { color: #00755d; }
    .warn { color: #b36a00; }
    .fail { color: #c0392b; }
    .muted { color: #8190a2; }

    .status-box {
        border-radius: 9px;
        padding: 0.75rem 0.9rem;
        margin-top: 0.7rem;
        font-size: 11px;
        line-height: 1.45;
    }

    .status-pass {
        background: #ecfbf6;
        border: 1px solid #bfeadb;
        color: #006b57;
    }

    .status-warn {
        background: #fff7e8;
        border: 1px solid #f1d69d;
        color: #8a5700;
    }

    .status-fail {
        background: #fff0ee;
        border: 1px solid #efc0ba;
        color: #a33125;
    }

    .status-info {
        background: #f2f6fa;
        border: 1px solid #dbe4ed;
        color: #53647a;
    }

    /* ---------- Verification ---------- */
    .verify-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #edf1f5;
        padding: 0.7rem 0;
        font-size: 11px;
    }

    .verify-row:last-child {
        border-bottom: none;
    }

    .verify-pending {
        color: #a86a00;
        font-size: 10px;
        font-weight: 600;
    }

    /* ---------- Buttons ---------- */
    /* ---------- Buttons ---------- */

div.stButton > button {
    border-radius: 7px;
    min-height: 38px;
    font-size: 12px;
    font-weight: 650;
    border: 1px solid #006b57;
    background: #ffffff;
    color: #006b57;
}

div.stButton > button:hover {
    border-color: #005946;
    background: #f0f8f6;
    color: #005946;
}

div.stButton > button[kind="primary"] {
    background: #006b57;
    border-color: #006b57;
    color: white;
}

div.stButton > button[kind="primary"]:hover {
    background: #005946;
    border-color: #005946;
    color: white;
}

    /* ---------- Inputs ---------- */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        border-radius: 7px;
    }


    div[data-baseweb="input"] {
    background-color: #ffffff !important;
    border: 1px solid #b8cfc8 !important;
    border-radius: 7px !important;
}

div[data-baseweb="input"]:focus-within {
    border: 1.5px solid #006b57 !important;
    box-shadow: 0 0 0 1px rgba(0, 107, 87, 0.12) !important;
}

div[data-baseweb="input"] input {
    background-color: #ffffff !important;
    color: #1f2937 !important;
    -webkit-text-fill-color: #1f2937 !important;
}

div[data-baseweb="input"] input::placeholder {
    color: #7a8793 !important;
    opacity: 1 !important;
}

/* Select boxes */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 1px solid #b8cfc8 !important;
    color: #1f2937 !important;
}

div[data-baseweb="select"] span {
    color: #1f2937 !important;
}

    label {
        font-size: 11px !important;
        color: #4e5d73 !important;
    }

    
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] label {
    color: #1f2937 !important;
}


/* ---------- Radio Buttons ---------- */

div[data-testid="stRadio"] label {
    color: #1f2937 !important;
}

div[data-testid="stRadio"] label p {
    color: #1f2937 !important;
}

div[data-testid="stRadio"] [role="radiogroup"] {
    color: #1f2937 !important;
}

div[data-testid="stRadio"] [role="radio"] {
    color: #006b57 !important;
}


    /* ---------- Responsive ---------- */
    @media (max-width: 800px) {
        .topbar {
            margin-left: -1rem;
            margin-right: -1rem;
            padding: 0 1rem;
        }

        .page-title {
            font-size: 23px;
        }
    }
</style>
""",
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
<div class="topbar">
    <div class="brand-wrap">
       <div class="brand-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="8" cy="16" r="3"/>
                <path d="M10.5 13.5 19 5"/>
                <path d="m16 8 2 2"/>
                <path d="m18 6 2 2"/>
            </svg>
        </div>
        <div class="brand">RentAssess</div>
        <div class="brand-divider"></div>
        <div class="portal">Underwriting Portal</div>
    </div>
    <div class="user">
        <strong>Kofi Mensah</strong><br>
        <small>Senior Underwriter</small>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_progress():
    labels = [
        "Applicant & Rent",
        "Financials & Documents",
        "Underwriting Risk",
        "Verification & Offer",
    ]

    # Build the HTML without indented multiline fragments.
    # This prevents Streamlit from interpreting the HTML as a code block.
    html = '<div class="progress-wrap"><div class="progress-row">'

    for i, label in enumerate(labels, start=1):
        state = get_step_state(i)
        symbol = "✓" if state == "complete" else str(i)

        html += (
            f'<div class="progress-item {state}">'
            f'<span class="progress-number">{symbol}</span>'
            f'{label}'
            f'</div>'
        )

    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)
