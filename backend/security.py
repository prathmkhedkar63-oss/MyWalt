import os
import time
import secrets
import hashlib
from typing import Optional, List, Dict
import jwt

SECRET_KEY_FILE = os.path.join(os.path.dirname(__file__), ".secret_key")

def get_secret_key() -> str:
    if os.path.exists(SECRET_KEY_FILE):
        with open(SECRET_KEY_FILE, "r") as f:
            return f.read().strip()
    key = secrets.token_hex(32)
    with open(SECRET_KEY_FILE, "w") as f:
        f.write(key)
    return key

SECRET_KEY = get_secret_key()
ALGORITHM = "HS256"

PASSWORD_FILE = os.path.join(os.path.dirname(__file__), ".password_hash")

# Password Hashing using PBKDF2 + SHA256 (Built-in, secure)
def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{key.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        if ':' not in stored_hash:
            return False
        salt_hex, key_hex = stored_hash.split(':', 1)
        key_hex = key_hex.lstrip('$')
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return secrets.compare_digest(key, new_key)
    except Exception:
        return False

def has_master_password() -> bool:
    return os.path.exists(PASSWORD_FILE)

def set_master_password(password: str) -> bool:
    hashed = hash_password(password)
    with open(PASSWORD_FILE, "w") as f:
        f.write(hashed)
    return True

def get_stored_password_hash() -> Optional[str]:
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r") as f:
            return f.read().strip()
    return None

def verify_master_password(password: str) -> bool:
    stored = get_stored_password_hash()
    if not stored:
        # Default password if not set: "admin"
        return password == "admin"
    return verify_password(password, stored)



# JWT Session Tokens
def create_token(data: dict, expires_in_seconds: int = 86400 * 7) -> str:
    payload = data.copy()
    payload.update({"exp": time.time() + expires_in_seconds})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except Exception:
        return None

# Write Access Tokens for File Modification Operations
def create_write_token(expires_in_seconds: int = 3600) -> str:
    """Create a signed JWT token granting file modification permissions."""
    payload = {
        "scope": "file_write_access",
        "iat": time.time(),
        "exp": time.time() + expires_in_seconds
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_write_token(token: Optional[str]) -> bool:
    """Verify if the provided token grants valid, unexpired write access."""
    if not token or not isinstance(token, str):
        return False
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded.get("scope") == "file_write_access"
    except Exception:
        return False

# Strict Path Sanitization to prevent Path Traversal Attacks
def sanitize_path(requested_path: str, allowed_roots: Optional[List[str]] = None) -> Optional[str]:
    try:
        if not requested_path or requested_path.strip() == "":
            return None
        
        abs_path = os.path.abspath(os.path.realpath(requested_path))
        
        if allowed_roots:
            is_allowed = False
            for root in allowed_roots:
                abs_root = os.path.abspath(os.path.realpath(root))
                if abs_path == abs_root or abs_path.startswith(abs_root + os.sep):
                    is_allowed = True
                    break
            if not is_allowed:
                return None
                
        return abs_path
    except Exception:
        return None

# Simple Rate Limiter for Login Attempts
FAILED_ATTEMPTS: Dict[str, Dict] = {}

def is_ip_locked(ip: str) -> bool:
    if ip in FAILED_ATTEMPTS:
        data = FAILED_ATTEMPTS[ip]
        if data["count"] >= 5:
            if time.time() - data["last_attempt"] < 900: # 15 minutes lockout
                return True
            else:
                FAILED_ATTEMPTS.pop(ip)
    return False

def record_failed_attempt(ip: str):
    now = time.time()
    if ip not in FAILED_ATTEMPTS:
        FAILED_ATTEMPTS[ip] = {"count": 1, "last_attempt": now}
    else:
        FAILED_ATTEMPTS[ip]["count"] += 1
        FAILED_ATTEMPTS[ip]["last_attempt"] = now

def reset_failed_attempts(ip: str):
    if ip in FAILED_ATTEMPTS:
        FAILED_ATTEMPTS.pop(ip)
