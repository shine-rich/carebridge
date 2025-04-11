
import sqlite3
import pandas as pd
from datetime import datetime, timezone
from config.constants import DB_FILE
from utils.encryption import decrypt_message, encrypt_message

def get_messages(session_id, start_date, end_date):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(
        """
        SELECT session_id, sender, message, timestamp, key_id
        FROM messages
        WHERE session_id = ? AND timestamp BETWEEN ? AND ?
        ORDER BY timestamp ASC
        """,
        conn,
        params=(
            session_id,
            datetime.combine(start_date, datetime.min.time()).isoformat(),
            datetime.combine(end_date, datetime.max.time()).isoformat()
        )
    )
    conn.close()
    if not df.empty:
        df["decrypted"] = df.apply(lambda row: decrypt_message(row["message"], row["key_id"]), axis=1)
    return df

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TEXT,
            sender TEXT,
            message TEXT,
            key_id TEXT
        )
    """)
    conn.commit()
    conn.close()

async def save_message(session_id, sender, message):
    encrypted_msg, key_id = encrypt_message(message, session_id)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, timestamp, sender, message, key_id) VALUES (?, ?, ?, ?, ?)",
              (session_id, datetime.now(timezone.utc).isoformat(), sender, encrypted_msg, key_id))
    conn.commit()
    conn.close()

# async def get_history(session_id):
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     c.execute("SELECT timestamp, sender, message, key_id FROM messages WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
#     rows = c.fetchall()
#     conn.close()
#     return [{"timestamp": t, "sender": s, "message": m, "key_id": k} for t, s, m, k in rows]

async def get_history(session_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT timestamp, sender, message, key_id FROM messages WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
    rows = c.fetchall()
    conn.close()

    history = []
    for t, s, m, k in rows:
        try:
            decrypted = decrypt_message(m, k)
        except Exception:
            decrypted = "[decryption failed]"
        history.append({
            "timestamp": t,
            "sender": s,
            "message": decrypted,
            "key_id": k,
            "decrypted": decrypted
        })

    return history
