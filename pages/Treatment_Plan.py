from components.sidebar import render_sidebar
import streamlit as st
from streamlit_elements import elements, mui, html, dashboard
from datetime import datetime, timedelta, timezone
from utils.db import get_messages
from utils.llm import generate_summary
from utils.treatment_utils import save_encrypted_plan, load_encrypted_plan
from config.constants import DEFAULT_SESSION

st.set_page_config(page_title="Treatment Plan", page_icon="📝")

render_sidebar()

st.title("📝 Counselor Treatment Plan")
if st.session_state.get("role") != "counselor":
    st.error("Access denied. Counselors only.")
    st.stop()

session_id = st.sidebar.text_input("Session ID", value=DEFAULT_SESSION)
default_start = (datetime.now(timezone.utc) - timedelta(days=3)).date()
default_end = datetime.now(timezone.utc).date()
start_date = st.sidebar.date_input("Start date", value=default_start)
end_date = st.sidebar.date_input("End date", value=default_end)
df = get_messages(session_id, start_date, end_date)

if df.empty:
    st.info("No messages found.")
else:
    for _, row in df.iterrows():
        st.markdown(f"**{row['sender']}** {row['decrypted']}")

st.subheader(f"💬 Chat Transcript for Session: '{session_id}'")
load_plan = load_encrypted_plan(session_id)

st.sidebar.markdown("### Load Plan")
if load_plan and "error" not in load_plan:
    st.sidebar.success("Plan loaded from file.")
else:
    load_plan = st.session_state.treatment_plan_data
    st.sidebar.info("No existing plan found.")

with st.expander("🧠 Treatment Plan Assistant", expanded=False):        
    # Define a clean grid layout (x, y, width, height)
    layout = [
        # Row 1: Top-wide cards
        dashboard.Item("case_recommendations", 0, 0, 4, 4),  # Wider progress summary
        dashboard.Item("risk_alert", 4, 0, 4, 1),        # Risk alert (full width)

        # Row 1: Top-wide cards
        dashboard.Item("progress_summary", 0, 0, 4, 2),  # Wider progress summary
        dashboard.Item("progress_chart", 4, 0, 4, 2),     # Progress card (left)
        dashboard.Item("goal_timeline", 0, 2, 4, 2.5),     # Progress card (left)

        # Row 2: Middle components
        dashboard.Item("risk_chart", 3.5, 0, 4, 2),     # Progress card (left)
        dashboard.Item("trigger_log", 3.5, 2, 6, 2),   # Wider CBT suggestions
        dashboard.Item("crisis_protocols", 0, 2, 3.5, 2),   # Wider CBT suggestions
        dashboard.Item("coping_strategies", 0, 0, 3.5, 2),   # Wider CBT suggestions

        # Row 3: Bottom cards          
        dashboard.Item("missed_activity_reasons", 0, 0, 4, 2.5),     # Progress card (left)
        dashboard.Item("adherence_chart", 4, 0, 5, 2.5),     # Progress card (left)
        dashboard.Item("auto_adjustments", 4, 2, 5, 2.5),     # Progress card (left)
        dashboard.Item("next_steps", 0, 6, 4, 2.5),     # Progress card (left)
        
        dashboard.Item("cbt_suggestions", 0, 2, 4, 2),   # Wider CBT suggestions
    ]
    
    # Display chat history
    for i, message in enumerate(st.session_state.treatment_chat):
        with st.chat_message(message["role"]):
            if isinstance(message.get("content"), str):
                # Simple text response
                st.write(message["content"])
            elif isinstance(message.get("content"), dict):
                # Structured response with MUI components
                with elements(f"response_{i}"):  # Unique key for each response
                    with dashboard.Grid(layout):
                        if message["content"]["type"] == "check-in":
                            with mui.Card(key="case_recommendations", sx={"p": 2, "mb": 2, "borderLeft": "4px solid #2196F3"}):
                                with mui.CardHeader(
                                    title="Next Case Recommendations",
                                    avatar=mui.icon.Assignment(color="primary"),
                                    action=mui.IconButton(mui.icon.Refresh)
                                ):
                                    pass
                                
                                # Current case data (would come from your database)
                                case = {
                                    "name": "Alex Chen",
                                    "age": 17,
                                    "goals": ["Reduce anxiety attacks", "Improve sleep routine"],
                                    "adherence_rate": 0.65,  # 65%
                                    "missed_activities": ["Journaling (3x)", "Medication (2x)"],
                                    "risk_level": "Medium"
                                }
                                
                                with mui.CardContent():
                                    # --- Student Summary Row ---
                                    with mui.Stack(direction="row", spacing=2, alignItems="center", sx={"mb": 2}):
                                        mui.Avatar("AC", sx={"bgcolor": "#1976D2"})
                                        with mui.Box():
                                            mui.Typography(case["name"], variant="h6")
                                            mui.Typography(
                                                f"Age {case['age']} • {case['risk_level']} Risk • {int(case['adherence_rate']*100)}% Adherence",
                                                variant="body2",
                                                color="text.secondary"
                                            )
                                    
                                    # --- Recommended Adjustments ---
                                    mui.Divider(text="Suggested Adjustments", sx={"my": 2})
                                    
                                    adjustments = [
                                        {
                                            "activity": "Journaling",
                                            "current": "Daily written entries",
                                            "suggestion": "Switch to voice memos 3x/week",
                                            "reason": "Missed 3x last week due to time constraints"
                                        },
                                        {
                                            "activity": "CBT Exercises",
                                            "current": "20-minute sessions",
                                            "suggestion": "Try 5-minute 'micro-CBT' exercises",
                                            "reason": "Low energy reported on weekdays"
                                        }
                                    ]
                                    
                                    for adj in adjustments:
                                        with mui.Alert(
                                            severity="info",
                                            icon=mui.icon.LightbulbOutline(),
                                            sx={"mb": 1, "alignItems": "flex-start"}
                                        ):
                                            with mui.Stack(spacing=0.5):
                                                mui.Typography(
                                                    f"{adj['activity']}: {adj['suggestion']}",
                                                    fontWeight="bold"
                                                )
                                                mui.Typography(
                                                    f"Instead of {adj['current']} • {adj['reason']}",
                                                    variant="body2"
                                                )
                                                with mui.Stack(direction="row", spacing=1, sx={"mt": 1}):
                                                    mui.Button(
                                                        "Apply This",
                                                        size="small",
                                                        variant="outlined",
                                                        startIcon=mui.icon.Check()
                                                    )
                                                    mui.Button(
                                                        "See Alternatives",
                                                        size="small",
                                                        startIcon=mui.icon.Search()
                                                    )
                                    
                                    # --- Quick Actions ---
                                    mui.Divider(text="Quick Actions", sx={"my": 2})
                                    with mui.Stack(direction="row", spacing=1):
                                        mui.Button(
                                            "View Full Case",
                                            variant="outlined",
                                            startIcon=mui.icon.FolderOpen()
                                        )
                                        mui.Button(
                                            "Start Session Notes",
                                            variant="contained",
                                            startIcon=mui.icon.Edit()
                                        )

                            # Risk Alert (Middle, full width)
                            with mui.Paper(
                                key="risk_alert",
                                sx={
                                    "mb": 2,
                                    "borderLeft": "4px solid #ff9800",
                                    "bgcolor": "#fff3e0",
                                    "p": 2,
                                    "height": "100%",
                                }
                            ):
                                mui.Typography("Risk Level: Medium", variant="h6")
                                mui.Typography("Monitor for increased hopelessness per last session.")

    # User input handling
    if prompt := st.chat_input("Ask about treatment plans..."):
        # Add user message to chat
        st.session_state.treatment_chat.append({"role": "user", "content": prompt})
        
        response_map = {
            "check-in": {"type": "check-in", "trigger": ["check-in", "checking-in"]},
            "tools": {"type": "tools_card", "trigger": ["tool", "recommend", "material"]},
            "cbt": {"type": "cbt_suggestions", "trigger": ["cbt", "technique", "exercise", "activity"]}
        }

        # Process query and generate appropriate response
        response = None
        prompt_lower = prompt.lower()
        
        for key, config in response_map.items():
            if any(trigger in prompt_lower for trigger in config["trigger"]):
                response = {"type": config["type"]}
                break
        
        if any(w in prompt_lower for w in ["full case", "progress", "summary"]):
            response = {
                "type": "progress_summary",
                "data": {
                    "progress": st.session_state.latest_entry["progress"],
                    "goals": st.session_state.latest_entry["goals"],
                    "next_steps": st.session_state.latest_entry["next_steps"]
                }
            }

        if not response:
            response = """I can help with:

            🔹 **Treatment Progress**  
            - "Show progress summary"  
            - "Latest updates"  

            🔹 **Therapeutic Tools**  
            - "What tools are available?"  
            - "Show resources"  

            🔹 **CBT Techniques**  
            - "Suggest CBT exercises"  
            - "Cognitive techniques"  

            🔹 **Risk Assessment**  
            - "Current risk level"  
            - "Any concerns?"  

            Try being specific like: "Show me the client's recent progress" or "What CBT techniques would help with anxiety?"
            """

        # Add response to chat
        st.session_state.treatment_chat.append({
            "role": "assistant", 
            "content": response if isinstance(response, dict) else response
        })
        
        # Force UI update
        st.rerun()
        
with st.expander("📋 Case Notes", expanded=False):
    if st.button("🤖 Auto-Fill from Chat"):
        with st.spinner("Fetching transcript and generating suggestions..."):
            df = get_messages(session_id, start_date=default_start, end_date=default_end)
            if df.empty:
                st.warning("No messages found for this session.")
            else:
                text = "\n".join(f"{row['sender'].title()}: {row['decrypted']}" for _, row in df.iterrows())

                st.session_state.treatment_plan_data["case_summary"] = st.text_area("Case Summary", height=150, value=load_plan.get("case_summary", "") if load_plan else "")
                st.session_state.treatment_plan_data["goals"] = st.text_area("Goals", value=load_plan.get("goals", "") if load_plan else "")
                st.session_state.treatment_plan_data["interventions"] = st.text_area("Planned Interventions", value=load_plan.get("interventions", "") if load_plan else "")
                st.session_state.treatment_plan_data["coping_strategies"] = st.text_area("Recommended Coping Strategies", value=load_plan.get("coping_strategies", "") if load_plan else "")

                st.header("📅 Follow-up Plan")
                next_session = st.date_input("Next Session Date", value=default_end)
                st.session_state.treatment_plan_data["followups"] = st.text_area("Next Steps", value=load_plan.get("followups", "") if load_plan else "")

                st.success(" populated with detailed demo data!")

    if st.button("💾 Save Treatment Plan"):
        save_encrypted_plan(session_id, st.session_state.treatment_plan_data)
        st.success("✅ Plan saved securely.")
