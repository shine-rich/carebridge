CHATBOX_HOST = "http://100.88.142.8"
CHATBOX_URL = f"{CHATBOX_HOST}:8503"
CHATBOX_IFRAME_URL = f"{CHATBOX_URL}/chat_login_ui.html"

DB_FILE = "carebridge.db"
BACKUP_DIR = "backups"
CASE_FORM_SAVE_DIR = "carebridge_case_forms"

# Define valid options for Suicidal Ideation
SUICIDAL_IDEATION_OPTIONS = ["No", "Passive", "Active with Plan", "Active without Plan"]
RISK_LEVEL_OPTIONS = ["Not Suicidal", "Low Risk", "Medium Risk", "High Risk", "Imminent Risk"]

TREATMENT_PLAN_SAVE_DIR = "carebridge_treatment_plans"
DEFAULT_SESSION = "demo_session"
SUMMARY_PROMPT = (
    "You are a compassionate school counselor assistant summarizing a brief chat session "
    "between a student and a counselor. Even if little is said, reflect on possible emotional context, "
    "relationship dynamics, and suggest follow-up actions. Use empathetic and supportive language."
)
