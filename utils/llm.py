import streamlit as st

from config.constants import SUMMARY_PROMPT, SUICIDAL_IDEATION_OPTIONS, RISK_LEVEL_OPTIONS
from llama_index.llms.openai_like import OpenAILike

def get_llm():
    return OpenAILike(
        api_base="http://127.0.0.1:11434/v1",
        model="gemma3:4b",
        api_key="sk-no-key-required",
        is_chat_model=True,
        stream=True,
        temperature=0.65,
        max_tokens=300,
        system_prompt=SUMMARY_PROMPT,
        timeout=30
    )

def generate_summary(transcript: str) -> str:
    llm = get_llm()

    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        for response in llm.stream_complete(f"Respond directly to: {transcript}"):
            full_response += response.delta
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    return full_response

# Response cleaner
def clean_response(text):
    removals = [
        "Okay, ", "Here's", "I'll", "Let me", "Based on",
        "natural response:", "empathetic response:",
        "framework:", "assessment:", "*", "\""
    ]
    for phrase in removals:
        text = text.replace(phrase, "")
    return text.strip().strip('"').strip(":").strip()

def get_form_value_from_convo(convo, form_value) -> str:
    return f"""You are a helpful assistant filling out a form. Extract the person's {form_value} from the following converstation in to input into the form. {convo}"""

def get_int_value_from_convo(convo, form_value) -> str:
    return f"""You are a helpful assistant filling out a form. Extract the person's {form_value} from the following converstation in to input into the form. {convo}"""

def get_risk_value_from_convo(convo) -> str:
    return f"""You are a helpful assistant filling out a form. Reply 0 if the person does not seem at risk based on the conversation. {convo}"""

def populate_form_fields_with_llm(chathistory):
    """Process chat history through LLM to populate form fields"""
    llm = get_llm()

    # Process each field with appropriate function
    st.session_state.case_form_data["first_name"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "First Name")
    )
    st.session_state.case_form_data["reason_for_contact"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Reason for Contact")
    )    
    st.session_state.case_form_data["brief_summary"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Brief Summary/Narrative")
    )
    st.session_state.case_form_data["next_session_date"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Next Session Date")
    )
    st.session_state.case_form_data["gender_identity"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Gender Identity")
    )
    st.session_state.case_form_data["preferred_pronouns"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Preferred Pronouns")
    )
    st.session_state.case_form_data["coping_strategies"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Current Coping Strategies")
    )
    st.session_state.case_form_data["goals"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Goals for This Session")
    )
    st.session_state.case_form_data["progress"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Progress Toward Previous Goals")
    )
    st.session_state.case_form_data["emergency_contact_name"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Emergency Contact Name")
    )
    st.session_state.case_form_data["relationship"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Relationship")
    )
    st.session_state.case_form_data["phone_number"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Phone Number")
    )
    st.session_state.case_form_data["previous_mental_health_history"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Previous Mental Health History")
    )
    st.session_state.case_form_data["follow_up_actions"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Follow-Up Actions")
    )

    # Handle numeric fields
    try:
        st.session_state.case_form_data["age"] = int(process_form_field(
            llm, get_int_value_from_convo(chathistory, "Age")
        ))
    except ValueError:
        st.session_state.case_form_data["age"] = 0
    
    # Process other string fields
    st.session_state.case_form_data["location"] = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Location (City, State)")
    )
    
    # Process special fields with options
    suicidal_response = process_form_field(
        llm, get_form_value_from_convo(chathistory, "Suicidal Ideation")
    )
    st.session_state.case_form_data["suicidal_ideation"] = (
        suicidal_response if suicidal_response in SUICIDAL_IDEATION_OPTIONS 
        else "No"
    )
    
    risk_response = process_form_field(
        llm, get_risk_value_from_convo(chathistory)
    )
    st.session_state.case_form_data["risk_level"] = (
        risk_response if risk_response in RISK_LEVEL_OPTIONS
        else "Medium Risk"
    )
    st.success("Case form populated with AI analysis.")

def process_form_field(llm, prompt):
    """Get cleaned response from LLM for form field population"""
    response = llm.complete(prompt).text
    return clean_response(response)

def populate_case_form_with_demo_data():
    # Populate Case Form data in session state with more realistic demo data
    st.session_state.case_form_data.update({
        "first_name": "Alex",
        "reason_for_contact": "Feeling overwhelmed with work and personal life balance.",
        "age": 29,
        "location": "San Francisco, CA",
        "gender_identity": "Non-binary",
        "preferred_pronouns": "They/Them",
        "suicidal_ideation": "Passive",
        "risk_level": "Medium Risk",
        "brief_summary": "Alex has been feeling overwhelmed due to increasing work pressure and personal responsibilities. They have expressed passive suicidal ideation but no specific plans or means.",
        "coping_strategies": "Meditation, journaling, and occasional walks.",
        "goals": "Develop better time management skills and find effective stress-relief techniques.",
        "progress": "Alex has started practicing mindfulness exercises and is working on setting boundaries at work.",
        "emergency_contact_name": "Jordan Smith",
        "relationship": "Friend",
        "phone_number": "555-1234",
        "previous_mental_health_history": "Previous episodes of anxiety managed with therapy.",
        "follow_up_actions": "Schedule next session, provide resources on stress management, follow up with emergency contact if necessary.",
        "next_session_date": "2025-11-15"
    })
