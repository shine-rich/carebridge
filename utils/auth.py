
import streamlit as st

USERS = {
    "counselor": {"password": "pass123", "role": "counselor"},
    "admin": {"password": "admin123", "role": "admin"},
}

def login():
    st.subheader("🔐 Login")
    with st.form("login_form", clear_on_submit=False):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
    if submitted:
        if user in USERS and USERS[user]["password"] == pw:
            st.session_state.logged_in = True
            st.session_state.username = user
            st.session_state.role = USERS[user]["role"]
            st.success("Logged in successfully.")
            st.rerun()
        else:
            st.error("Invalid credentials.")
