from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timezone
from typing import Optional
import secrets
import jwt
from uuid import UUID

from src.models.users_models import UserRegister, UserLogin, ApiKeyPublic
from src.utils.mongo_db.conexion_mongo import connect_to_mongodb
from src.security.hashing import hash_password, verify_password, hash_apikey
from src.security.jwt import create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")  # para Swagger

# ----------------- helpers -----------------


def _get_collections():
    db, users = connect_to_mongodb()
    apikeys = db["apikeys"]
    return db, users, apikeys


def _create_and_store_apikey_for(email: str) -> str:
    """
    Crea una API key nueva (texto plano para el usuario) y guarda su hash en DB.
    Retorna el valor PLANO (se muestra solo en este momento).
    """
    _, _, apikeys = _get_collections()

    # Generar cadena segura (URL-safe)
    new_key = secrets.token_urlsafe(32)
    key_hash = hash_apikey(new_key)

    # Eliminamos API keys antiguas del mismo usuario (si quieres una sola activa)
    apikeys.delete_many({"user_email": email})

    apikeys.insert_one(
        {
            "user_email": email,
            "key_hash": key_hash,
            "createdAt": datetime.now(timezone.utc),
        }
    )
    return new_key


# ----------------- dependencias -----------------


def get_current_user_email(token: str = Depends(oauth2)) -> str:
    try:
        payload = decode_access_token(token)
        print("payload decodficicado: ", payload)
        email: Optional[str] = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido (sin sub)")
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")


# ----------------- endpoints -----------------


@router.post("/register")
def register(payload: UserRegister):
    _, users, _ = _get_collections()

    if users.find_one({"email": payload.email}):
        raise HTTPException(status_code=409, detail="Ese email ya está registrado")

    user_doc = {
        "user_name": payload.user_name,
        "email": payload.email,
        "password": hash_password(payload.password),  # hash
        "createdAt": datetime.now(timezone.utc),
    }
    users.insert_one(user_doc)

    # Crear la API key del usuario y retornarla aparte (opcional)
    # Si quieres mostrarla aquí, puedes devolverla en otro campo

    return {
        "username ": payload.user_name,
        "email ": payload.email,
        "password": payload.password,
    }


def find_user_existing(user) -> str:
    _, users, _ = _get_collections()
    user = users
    return user


@router.post("/login")
def login(payload: UserLogin):
    _, users, _ = _get_collections()
    user = users.find_one({"email": payload.email})
    print(f"email encontrado para  el login: {payload.email}")
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    users.find_one({"id": payload.user_name})

    print(f"name del usuario para el login: {payload.user_name}")
    
    # id_usuario= users.find_one({"id": payload.id})
    # print(f"id del usuario: {id_usuario}")
    
    token = create_access_token(
        # id_user=user_id,
        user_name=str(user["user_name"]),
        email=str(user["email"]),
        minutes=3,
    )
    # user = users.find_one({"user_name": payload.user_name})

    print(f"token imprimido: {token}")
    decode_token = decode_access_token(token)
    print(f"token descomprimido: {decode_token}")
    # print(f"el nombre del usuario encontrado: {user}\n")
    return {"access_token": token, "token_type": "bearer", "expires_in_minutes": 3}


@router.post("/apikey/rotate", response_model=ApiKeyPublic)
def rotate_api_key(current_email: str = Depends(get_current_user_email)):
    """
    Crea una nueva API key para el usuario autenticado.
    Devuelve el valor PLANO de la nueva key (guarda el hash en DB).
    """
    new_plain_key = _create_and_store_apikey_for(current_email)
    return ApiKeyPublic(api_key=new_plain_key)


@router.get("/apikey/exists")
def has_api_key(current_email: str = Depends(get_current_user_email)):
    """
    Retorna si el usuario tiene una API key (no devuelve el valor).
    """
    _, _, apikeys = _get_collections()
    exists = apikeys.find_one({"user_email": current_email}) is not None
    return {"has_api_key": exists}
