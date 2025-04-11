import streamlit as st
from utils.auth import login
from utils.session_state import init_state
from components.sidebar import render_sidebar

st.set_page_config(page_title="CareBridge", page_icon="💬", layout="centered")

st.title("👋 Welcome to CareBridge")
init_state()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.info("🔐 Please login to continue")
    login()
    st.stop()

# render_sidebar()

role = st.session_state.get("role", "unknown")
username = st.session_state.get("username", "Guest")

st.success(f"✅ Logged in as **{username}** ({role})")

if role == "counselor":
    st.markdown("### Navigate to your tools:")
    st.page_link("pages/Case_Form.py", label="📊 View Transcript & Summary")
    st.page_link("pages/Treatment_Plan.py", label="📝 Treatment Plan")
elif role == "admin":
    st.markdown("### Admin Options:")
    st.page_link("pages/Backup_Restore.py", label="💾 Backup & Restore")
else:
    st.warning("No tools assigned to this role.")
