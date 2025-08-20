import os
import jwt
from datetime import datetime, timedelta, timezone

JWT_SECRET = os.getenv("JWT_SECRET", "cambia-esto-en-produccion")
JWT_ALGORITHM = "HS256"

def create_access_token(subject: str, minutes: int = 3) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {"sub": subject, "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    # Deja que las excepciones de PyJWT salgan y se manejen arriba (dependencia)

    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
