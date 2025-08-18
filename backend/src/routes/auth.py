from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta, timezone
from src.models.users_models import User, UserLogin, UserPublic
from src.utils.mongo_db.conexion_mongo import connect_to_mongodb
from src.security.hashing import hash_password, verify_password
from src.security.jwt import create_access_token, decode_access_token
from pydantic import EmailStr
from typing import Optional
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=UserPublic)
def register(payload: User):
    db, collection = connect_to_mongodb()

    # ¿ya existe el email?
    if collection.find_one({"email": payload.email}):
        raise HTTPException(status_code=409, detail="Email ya registrado")

    user_doc = {
        "user_name": payload.user_name,
        "email": payload.email,
        "password": hash_password(payload.password),  # guardamos hash
        "createdAt": datetime.now(timezone.utc)
    }
    collection.insert_one(user_doc)

    return UserPublic(user_name=payload.user_name, email=payload.email)

@router.post("/login")
def login(payload: UserLogin):
    _, collection = connect_to_mongodb()
    user = collection.find_one({"email": payload.email})
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Token válido por 2 horas (cámbialo si quieres)
    token = create_access_token(subject=str(user["email"]), expires_delta=timedelta(hours=2))
    return {"access_token": token, "token_type": "bearer"}

# Ejemplo de dependencia para rutas protegidas
def get_current_user_email(token: str = Depends(oauth2)) -> EmailStr:
    try:
        payload = decode_access_token(token)
        email: Optional[str] = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
        return EmailStr(email)
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
