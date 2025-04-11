
# 🧠 CareBridge - Counselor Support Platform

CareBridge is a secure, modular, AI-powered dashboard for high school counselors to:

- 🧾 View and summarize chat transcripts
- 📝 Manage treatment plans
- 💬 Communicate with students via WebSocket chat
- 🔒 Backup and restore sensitive data
- 👩‍⚕️ Empower decisions with local LLM summarization

---

## 🚀 Features

- Role-based login (Counselor/Admin)
- Secure AES-encrypted treatment plan storage
- FastAPI backend with WebSocket chat
- Streamlit dashboards with summaries via LLM
- Modular Python project layout
- Auto-refresh, export, and backup functionality

---

## 🔐 Encrypted Storage

- Treatment plans are saved using AES-GCM with PBKDF2-derived keys.
- Backups are `.enc` encrypted files stored locally.

---

## ✍️ Summary Generation

LLM-powered summaries are generated from chat transcripts using your local model. Prompting is configurable in `config/constants.py`.

---

## 💾 Backup/Restore

Encrypted `.enc` backups can be created and restored from the Admin dashboard.

---

## ✅ To Do / Optional Enhancements

- Add user registration
- Encrypt chat messages directly
- Expand role-based permissions
- Add multi-language support
