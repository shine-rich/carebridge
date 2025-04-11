import base64
import secrets
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from config.constants import DB_FILE
import sqlite3

def ensure_session_salt(session_id: str) -> str:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS session_keys (session_id TEXT PRIMARY KEY, salt TEXT)")
    c.execute("SELECT salt FROM session_keys WHERE session_id = ?", (session_id,))
    row = c.fetchone()
    if row:
        conn.close()
        return row[0]
    salt = base64.b64encode(secrets.token_bytes(16)).decode()
    c.execute("INSERT INTO session_keys (session_id, salt) VALUES (?, ?)", (session_id, salt))
    conn.commit()
    conn.close()
    return salt

def derive_key(password: str, salt_b64: str) -> bytes:
    salt = base64.b64decode(salt_b64)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_message(message: str, session_id: str, password="carebridge-default"):
    salt_b64 = ensure_session_salt(session_id)
    key = derive_key(password, salt_b64)
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ct = aesgcm.encrypt(nonce, message.encode(), None)
    encrypted_b64 = base64.b64encode(nonce + ct).decode()
    return encrypted_b64, salt_b64

def decrypt_message(encrypted_b64: str, salt_b64: str, password="carebridge-default"):
    key = derive_key(password, salt_b64)
    encrypted = base64.b64decode(encrypted_b64)
    nonce = encrypted[:12]
    ct = encrypted[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None).decode()
