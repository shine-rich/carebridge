from components.sidebar import render_sidebar

import streamlit as st
import os
from datetime import datetime, timezone
from utils.encryption import decrypt_message  # reused for validation if needed
from config.constants import DB_FILE, BACKUP_DIR

os.makedirs(BACKUP_DIR, exist_ok=True)

st.set_page_config(page_title="Admin: Backup & Restore", page_icon="💾", layout="centered")
# render_sidebar()
st.title("🧑‍💼 Admin: Backup & Restore Panel")

# Confirm role
if st.session_state.get("role") != "admin":
    st.error("Access denied. Admins only.")
    st.stop()

# Backup section
st.header("🧱 Backup Current Data")
timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
backup_file = f"{BACKUP_DIR}/chat_backup_{timestamp}.enc"

if st.button("📦 Create Backup"):
    try:
        os.system(f"python3 restore_backup.py --backup --db {DB_FILE} --out {backup_file}")
        st.success(f"Backup saved as: {backup_file}")
    except Exception as e:
        st.error(f"Backup failed: {e}")

# Restore section
st.header("♻️ Restore From Backup")
uploaded = st.file_uploader("Upload .enc backup file", type=["enc"])

if uploaded and st.button("🛠 Restore Backup"):
    restore_path = f"{BACKUP_DIR}/restore_temp.enc"
    with open(restore_path, "wb") as f:
        f.write(uploaded.read())
    try:
        os.system(f"python3 restore_backup.py --restore --in {restore_path} --db {DB_FILE}")
        st.success("✅ Database restored successfully.")
    except Exception as e:
        st.error(f"Restore failed: {e}")
