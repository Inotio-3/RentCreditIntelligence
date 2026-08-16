import streamlit as st


def screen_profile():
    st.markdown(
        '<div class="page-title">RentAssess</div>',
        unsafe_allow_html=True,
    )
    st.info(
        "Welcome, Let's get started "
        
    )

    st.markdown(
        '<div class="page-subtitle">'
        "Select the primary applicant's profile to initiate the underwriting "
        "and credit assessment path"
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        selected = st.session_state.applicant_type == "Salaried / Employed"
        st.markdown(
            f"""
            <div class="profile-card {'selected' if selected else ''}">
                <div class="profile-icon">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M4 19V5a2 2 0 0 1 2-2h8l6 6v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2Z"/>
                        <path d="M14 3v6h6"/>
                        <path d="M8 13h8M8 17h5"/>
                    </svg>
            </div>
                <div class="profile-name">Salaried / Employed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Select Salaried", use_container_width=True):
            st.session_state.applicant_type = "Salaried / Employed"
            st.rerun()

    with col2:
        selected = st.session_state.applicant_type == "Business Owner / Self-Employed"
        st.markdown(
            f"""
            <div class="profile-card {'selected' if selected else ''}">
                <div class="profile-icon">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M3 10h18"/>
                        <path d="M5 10v10h14V10"/>
                        <path d="M4 10l2-6h12l2 6"/>
                        <path d="M9 20v-6h6v6"/>
                    </svg>
            </div>
                <div class="profile-name">Business Owner / Self-Employed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Select Business", use_container_width=True):
            st.session_state.applicant_type = "Business Owner / Self-Employed"
            st.rerun()
        
        

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(
        "Begin Assessment  →",
        type="primary",
        use_container_width=False,
        disabled=st.session_state.applicant_type is None,
    ):
        st.session_state.step = 1
        st.rerun()

    if st.session_state.applicant_type is None:
        st.info("Select an applicant profile above to begin.")
