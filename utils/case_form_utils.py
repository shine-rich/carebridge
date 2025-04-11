import os
import json
import base64
import secrets
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from config.constants import CASE_FORM_SAVE_DIR

os.makedirs(CASE_FORM_SAVE_DIR, exist_ok=True)

def derive_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def save_encrypted_form(session_id: str, plan_data: dict, password: str = "carebridge-case-form"):
    salt = secrets.token_bytes(16)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)

    plan_json = json.dumps(plan_data).encode()
    ct = aesgcm.encrypt(nonce, plan_json, None)

    bundle = {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ct).decode()
    }
    with open(f"{CASE_FORM_SAVE_DIR}/plan_{session_id}.enc", "w") as f:
        json.dump(bundle, f)

def load_encrypted_form(session_id: str, password: str = "carebridge-case-form"):
    try:
        with open(f"{CASE_FORM_SAVE_DIR}/plan_{session_id}.enc", "r") as f:
            bundle = json.load(f)

        salt = base64.b64decode(bundle["salt"])
        nonce = base64.b64decode(bundle["nonce"])
        ct = base64.b64decode(bundle["ciphertext"])
        key = derive_key(password, salt)

        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ct, None)
        return json.loads(plaintext)
    except FileNotFoundError:
        return None
    except Exception as e:
        return {"error": str(e)}
