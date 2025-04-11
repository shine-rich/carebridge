import streamlit as st

st.set_page_config(page_title="Counselor Chat", layout="wide")
st.title("👩‍⚕️ Counselor WebSocket Chat")

st.markdown("This interface embeds your existing real-time chat UI:")

def suggest_cbt_techniques(student_message):
    # Hardcoded technique database
    cbt_library = {
        "anxiety": [
            "🌬️ 4-7-8 Breathing: Inhale 4s, hold 7s, exhale 8s",
            "📝 Thought Challenging: 'What evidence supports this worry?'"
        ],
        "depression": [
            "🎯 Behavioral Activation: Schedule 1 enjoyable activity today",
            "🌈 Positive Affirmations: 'I am capable of overcoming challenges'"
        ],
        "anger": [
            "🕑 Time-Out Technique: Pause for 10 minutes before responding",
            "📊 Cost-Benefit Analysis: List pros/cons of angry reaction"
        ]
    }

    # Mock theme detection
    detected_themes = []
    if any(word in student_message.lower() for word in ["worry", "anxious"]):
        detected_themes.append("anxiety")
    if any(word in student_message.lower() for word in ["sad", "hopeless"]):
        detected_themes.append("depression")
    if any(word in student_message.lower() for word in ["angry", "frustrated"]):
        detected_themes.append("anger")

    # Display suggestions
    with st.container(border=True):
        st.subheader("🧠 Recommended CBT Techniques")
        
        if detected_themes:
            for theme in detected_themes[:2]:  # Show max 2 themes
                st.markdown(f"**{theme.title()} Interventions:**")
                for technique in cbt_library.get(theme, [])[:2]:  # Show 2 techniques per theme
                    st.write(f"- {technique}")
                st.divider()
        else:
            st.write("💡 General Wellness Suggestion:")
            st.write("- 🚶♂️ 5-Minute Mindful Walk: Focus on sensory experiences")

def display_risk_dashboard(student_message):
    # Hardcoded risk keywords and demo scoring
    risk_keywords = {
        "suicide": 3,
        "harm": 2,
        "self-harm": 3,
        "hopeless": 1,
        "worthless": 1
    }
    
    # Simulate risk detection
    detected_risks = {word: count for word, count in risk_keywords.items() 
                     if word in student_message.lower()}
    
    # Calculate mock risk score
    risk_score = sum(detected_risks.values()) 
    risk_level = "Low" if risk_score < 2 else "Medium" if risk_score < 4 else "High"
    
    # Create columns layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Risk level indicator with color coding
        st.markdown(f"""
        <div style='padding: 1rem; border-radius: 0.5rem; 
                    background-color: {"#ffcccc" if risk_level == "High" else 
                                      "#fff3cd" if risk_level == "Medium" else 
                                      "#d4edda"};
                    text-align: center;'>
            <h3 style='color: {"#721c24" if risk_level == "High" else 
                              "#856404" if risk_level == "Medium" else 
                              "#155724"};'>
                Risk Level: {risk_level}
            </h3>
            <p>Score: {risk_score}/10</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Detected keywords display
        if detected_risks:
            st.write("**Detected Risk Indicators:**")
            for word, severity in detected_risks.items():
                st.write(f"- {word.capitalize()} (severity: {'⭐' * severity})")
        else:
            st.success("✅ No high-risk indicators detected")

def display_sentiment_analysis(student_message):
    # Hardcoded sentiment values for demo
    mock_sentiment = {
        "label": "POSITIVE",  # Could be NEGATIVE/NEUTRAL
        "score": 0.92  # Confidence score between 0-1
    }

    # Display as a metric card
    st.metric("Current Mood 🌟", 
            f"{mock_sentiment['label'].title()} ({mock_sentiment['score']:.2f})",
            delta="improving" if mock_sentiment['label'] == "POSITIVE" else "declining")

def display_conversation_themes(chat_history):
    # Hardcoded theme detection
    theme_keywords = {
        "Academic Stress": ["school", "exam", "homework"],
        "Family Dynamics": ["parent", "family", "mom", "dad"],
        "Social Anxiety": ["friend", "social", "crowd"],
        "Self-Esteem": ["worth", "confidence", "ugly"]
    }
    
    # Mock analysis
    detected_themes = []
    for theme, keywords in theme_keywords.items():
        if any(keyword in chat_history.lower() for keyword in keywords):
            detected_themes.append(theme)
    
    # Display in columns
    with st.expander("🔍 Conversation Themes Analysis", expanded=True):
        if detected_themes:
            cols = st.columns(2)
            for i, theme in enumerate(detected_themes[:4]):  # Max 4 themes
                with cols[i % 2]:
                    st.markdown(f"""
                    <div style='padding:0.5rem; margin:0.5rem 0; 
                                border-radius:0.3rem; background:#f0f2f6;'>
                        <b>{theme}</b>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.write("🌟 Primary Theme: General Well-being Check-in")

# Optionally display session info or controls on the side
st.sidebar.header("Session Tools")
st.sidebar.write("💡 Launches WebSocket UI in iframe.")
st.sidebar.button("Refresh Chat")

# Create two columns for side-by-side containers
col1, col2 = st.columns(2)

with col1:
    # Embed the chatbot HTML inside an iframe
    st.components.v1.iframe(src="http://localhost:8503/chat_login_ui.html", height=700, width=1000)

with col2:
    st.subheader("Live Insights 🔍")
    with st.expander("Emotional State & Risk Analysis", expanded=False):
        display_sentiment_analysis("")  # Custom function
        display_risk_dashboard("")
    
    st.subheader("Tools & Resources 🛠️")
    with st.expander("CBT Techniques", expanded=False):
        suggest_cbt_techniques("")      # Custom function
    
    with st.expander("Quick Actions", expanded=False):
        counselor_note = st.text_input("Add Session Note")
        st.button("🚨 Escalate Case")
        st.button("📝 Save Note to Form")
    
    st.subheader("Session Themes 📌")
    display_conversation_themes("")         # Custom function
    
    st.subheader("Sources")
    source_links = [
        "https://www.nimh.nih.gov/health/publications/stress/index.shtml",
        "https://www.apa.org/topics/resilience",
        "https://www.mind.org.uk/information-support/types-of-mental-health-problems/"
    ]
    source_titles = [
        "NIMH Coping with Stress",
        "APA Building Your Resilience",
        "Mind Coping with Mental Health Problems"
    ]
    i = 0
    sources_row = st.columns(len(source_links))
    for col in sources_row:
        with col.container(height=50):
            st.markdown(f'<a href="{source_links[i]}" target="_blank">"{source_titles[i]}"</a>', unsafe_allow_html=True)
        i += 1
