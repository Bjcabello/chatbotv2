import os
import jwt
from datetime import datetime, timedelta, timezone

JWT_SECRET = "JWT_SECRET"
JWT_ALGORITHM = "HS256"  
#68a7b2e5cd810dcc67564734
#68a7b2e5cd810dcc67564734


def create_access_token( user_id: str, email: str,  expires_delta: timedelta = timedelta(minutes=5)) -> str:
    exp = datetime.now(timezone.utc) + expires_delta
    payload = {
        # "id_user": id_user,
        # "user_name": user_name,
        "sub (id del usuario)": user_id,
        "email": email,
        "exp": exp,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    # Deja que las excepciones de PyJWT salgan y se manejen arriba (dependencia)

    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
