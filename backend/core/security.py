import hashlib

def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty")
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return hash_password(plain) == hashed
    except Exception:
        return False