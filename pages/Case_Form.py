from components.sidebar import render_sidebar
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from utils.session_state import init_state
from utils.auth import login
from utils.db import get_messages
from utils.llm import generate_summary, populate_form_fields_with_llm, populate_case_form_with_demo_data
from config.constants import DEFAULT_SESSION, SUICIDAL_IDEATION_OPTIONS, RISK_LEVEL_OPTIONS
from utils.case_form_utils import save_encrypted_form, load_encrypted_form

st.set_page_config(page_title="Counselor Dashboard", page_icon="🧑‍⚕️", layout="wide")

# render_sidebar()

if not st.session_state.logged_in:
    login()
    st.stop()

st.sidebar.markdown(f"Logged in as: <span style='color:green'>{st.session_state.username}</span>", unsafe_allow_html=True)
if st.sidebar.button("🔒 Logout"):
    for key in ["logged_in", "username", "role"]:
        st.session_state.pop(key, None)
    st.rerun()

# Sidebar Filters
st.sidebar.header("📋 Filters")
session_id = st.sidebar.text_input("Session ID", value=DEFAULT_SESSION)
load_plan = load_encrypted_form(session_id)
default_start = (datetime.now(timezone.utc) - timedelta(days=3)).date()
default_end = datetime.now(timezone.utc).date()
start_date = st.sidebar.date_input("Start date", value=default_start)
end_date = st.sidebar.date_input("End date", value=default_end)
autorefresh = st.sidebar.checkbox("🔄 Auto-refresh every 5 seconds")

st.title("🧑‍⚕️ Case Form Dashboard")
st.subheader(f"💬 Chat Transcript for Session: '{session_id}'")

df = get_messages(session_id, start_date, end_date)

if df.empty:
    st.info("No messages found.")
else:
    for _, row in df.iterrows():
        st.markdown(f"**{row['sender']}** {row['decrypted']}")

with st.expander("🧠 AI Summary", expanded=True):
    if st.button("🤖 Auto-Fill from Chat", key="ai_summary"):
        if not df.empty:
            with st.spinner("Generating AI summary..."):
                transcript = "\n".join(f"{r['sender'].title()}: {r['decrypted']}" for _, r in df.iterrows())
                summary = generate_summary(transcript)
                st.info(summary)
            st.success("✅ Summary complete.")
        else:
            st.warning("No messages to summarize.")

with st.expander("🧠 AI Case Form", expanded=False):
    if st.button("🤖 Auto-Fill from Chat (DEMO)", key="ai_case_form_demo"):
        with st.spinner("Fetching transcript and populating case form..."):
            df = get_messages(session_id, start_date=default_start, end_date=default_end)
            if df.empty:
                st.warning("No messages found for this session.")
            else:
                text = "\n".join(f"{row['sender'].title()}: {row['decrypted']}" for _, row in df.iterrows())
                populate_case_form_with_demo_data()

                col_b1, col_b2 = st.columns([0.5, 0.5], gap="small")

                with col_b1:
                    st.session_state.case_form_data["first_name"] = st.text_input("First Name", value=st.session_state.case_form_data["first_name"])
                    st.session_state.case_form_data["reason_for_contact"] = st.text_input("Reason for Contact", value=st.session_state.case_form_data["reason_for_contact"])
                    st.session_state.case_form_data["age"] = st.number_input("Age", value=st.session_state.case_form_data["age"])
                    st.session_state.case_form_data["location"] = st.text_input("Location (City, State)", value=st.session_state.case_form_data["location"])
                    st.session_state.case_form_data["gender_identity"] = st.text_input("Gender Identity", value=st.session_state.case_form_data["gender_identity"])
                    st.session_state.case_form_data["preferred_pronouns"] = st.text_input("Preferred Pronouns", value=st.session_state.case_form_data["preferred_pronouns"])
                    st.session_state.case_form_data["suicidal_ideation"] = st.selectbox(
                        "Suicidal Ideation",
                        SUICIDAL_IDEATION_OPTIONS,
                        index=SUICIDAL_IDEATION_OPTIONS.index(st.session_state.case_form_data["suicidal_ideation"])
                    )
                    st.session_state.case_form_data["risk_level"] = st.selectbox(
                        "Risk Level",
                        RISK_LEVEL_OPTIONS,
                        index=RISK_LEVEL_OPTIONS.index(st.session_state.case_form_data["risk_level"])
                    )
                with col_b2:
                    st.session_state.case_form_data["brief_summary"] = st.text_area("Brief Summary/Narrative", value=st.session_state.case_form_data["brief_summary"])
                    st.session_state.case_form_data["coping_strategies"] = st.text_area("Current Coping Strategies", value=st.session_state.case_form_data["coping_strategies"])
                    st.session_state.case_form_data["goals"] = st.text_area("Goals for This Session", value=st.session_state.case_form_data["goals"])
                    st.session_state.case_form_data["progress"] = st.text_area("Progress Toward Previous Goals", value=st.session_state.case_form_data["progress"])
                    st.session_state.case_form_data["emergency_contact_name"] = st.text_input("Emergency Contact Name", value=st.session_state.case_form_data["emergency_contact_name"])
                    st.session_state.case_form_data["relationship"] = st.text_input("Relationship", value=st.session_state.case_form_data["relationship"])
                    st.session_state.case_form_data["phone_number"] = st.text_input("Phone Number", value=st.session_state.case_form_data["phone_number"])
                    st.session_state.case_form_data["previous_mental_health_history"] = st.text_area("Previous Mental Health History", value=st.session_state.case_form_data["previous_mental_health_history"])
                    st.session_state.case_form_data["follow_up_actions"] = st.text_area("Follow-Up Actions", value=st.session_state.case_form_data["follow_up_actions"])
                    st.session_state.case_form_data["next_session_date"] = st.text_input("Next Session Date", value=st.session_state.case_form_data["next_session_date"])

    if st.button("🤖 Auto-Fill from Chat", key="ai_case_form"):
        with st.spinner("Fetching transcript and populating case form..."):
            df = get_messages(session_id, start_date=default_start, end_date=default_end)
            if df.empty:
                st.warning("No messages found for this session.")
            else:
                text = "\n".join(f"{row['sender'].title()}: {row['decrypted']}" for _, row in df.iterrows())
                populate_form_fields_with_llm(text)

                col_b1, col_b2 = st.columns([0.5, 0.5], gap="small")

                with col_b1:
                    st.session_state.case_form_data["first_name"] = st.text_input("First Name", value=st.session_state.case_form_data["first_name"])
                    st.session_state.case_form_data["reason_for_contact"] = st.text_input("Reason for Contact", value=st.session_state.case_form_data["reason_for_contact"])
                    st.session_state.case_form_data["age"] = st.number_input("Age", value=st.session_state.case_form_data["age"])
                    st.session_state.case_form_data["location"] = st.text_input("Location (City, State)", value=st.session_state.case_form_data["location"])
                    st.session_state.case_form_data["gender_identity"] = st.text_input("Gender Identity", value=st.session_state.case_form_data["gender_identity"])
                    st.session_state.case_form_data["preferred_pronouns"] = st.text_input("Preferred Pronouns", value=st.session_state.case_form_data["preferred_pronouns"])
                    st.session_state.case_form_data["suicidal_ideation"] = st.selectbox(
                        "Suicidal Ideation",
                        SUICIDAL_IDEATION_OPTIONS,
                        index=SUICIDAL_IDEATION_OPTIONS.index(st.session_state.case_form_data["suicidal_ideation"])
                    )
                    st.session_state.case_form_data["risk_level"] = st.selectbox(
                        "Risk Level",
                        RISK_LEVEL_OPTIONS,
                        index=RISK_LEVEL_OPTIONS.index(st.session_state.case_form_data["risk_level"])
                    )
                with col_b2:
                    st.session_state.case_form_data["brief_summary"] = st.text_area("Brief Summary/Narrative", value=st.session_state.case_form_data["brief_summary"])
                    st.session_state.case_form_data["coping_strategies"] = st.text_area("Current Coping Strategies", value=st.session_state.case_form_data["coping_strategies"])
                    st.session_state.case_form_data["goals"] = st.text_area("Goals for This Session", value=st.session_state.case_form_data["goals"])
                    st.session_state.case_form_data["progress"] = st.text_area("Progress Toward Previous Goals", value=st.session_state.case_form_data["progress"])
                    st.session_state.case_form_data["emergency_contact_name"] = st.text_input("Emergency Contact Name", value=st.session_state.case_form_data["emergency_contact_name"])
                    st.session_state.case_form_data["relationship"] = st.text_input("Relationship", value=st.session_state.case_form_data["relationship"])
                    st.session_state.case_form_data["phone_number"] = st.text_input("Phone Number", value=st.session_state.case_form_data["phone_number"])
                    st.session_state.case_form_data["previous_mental_health_history"] = st.text_area("Previous Mental Health History", value=st.session_state.case_form_data["previous_mental_health_history"])
                    st.session_state.case_form_data["follow_up_actions"] = st.text_area("Follow-Up Actions", value=st.session_state.case_form_data["follow_up_actions"])
                    st.session_state.case_form_data["next_session_date"] = st.text_input("Next Session Date", value=st.session_state.case_form_data["next_session_date"])

                st.success("Case form populated with detailed demo data!")

    if st.button("💾 Save Case Form"):
        save_encrypted_form(session_id, st.session_state.case_form_data)
        st.success("✅ Plan saved securely.")

if autorefresh:
    st.rerun()
