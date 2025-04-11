import streamlit as st

def render_sidebar():
    if not st.session_state.get("logged_in"):
        return

    st.sidebar.markdown("## 🧭 Navigation")
    role = st.session_state.get("role", "")

    if role == "counselor":
        st.sidebar.page_link("pages/Case_Form.py", label="📊 Dashboard")
        st.sidebar.page_link("pages/Treatment_Plan.py", label="📝 Treatment Plan")
    elif role == "admin":
        st.sidebar.page_link("pages/Backup_Restore.py", label="💾 Backup & Restore")

    st.sidebar.page_link("Home.py", label="🏠 Home")
