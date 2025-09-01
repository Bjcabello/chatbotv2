from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timezone
from typing import Optional
import secrets
import jwt
import uuid
import time
from src.models.users_models import UserRegister, UserLogin, ApiKeyPublic
from src.utils.mongo_db.conexion_mongo import connect_to_mongodb
from src.security.hashing import hash_password, verify_password, hash_apikey
from src.security.jwt import create_access_token, decode_access_token
from fastapi.security import APIKeyHeader
from passlib.context import CryptContext
from datetime import datetime, timedelta


db, users = connect_to_mongodb()
# apikeys = db["apikeys"]
api_keys_collection = db["api_keys"]

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")  # para Swagger

def generate_api_key():
    return secrets.token_hex(32)  # 64 caracteres, seguro

# API Key header
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


# ----------------- helpers -----------------


def _get_collections():
    db, users = connect_to_mongodb()
    apikeys = db["apikeys"]
    return db, users, apikeys


# def _create_and_store_apikey_for(email: str) -> str:
#     """
#     Crea una API key nueva (texto plano para el usuario) y guarda su hash en DB.
#     Retorna el valor PLANO (se muestra solo en este momento).
#     """
#     _, _, apikeys = _get_collections()

#     # Generar cadena segura (URL-safe)
#     new_key = secrets.token_urlsafe(32)
#     key_hash = hash_apikey(new_key)

#     # Eliminamos API keys antiguas del mismo usuario (si quieres una sola activa)
#     apikeys.delete_many({"user_email": email})

#     apikeys.insert_one(
#         {
#             "user_email": email,
#             "key_hash": key_hash,
#             "createdAt": datetime.now(timezone.utc),
#         }
#     )
#     return new_key


# ----------------- dependencias -----------------


# def get_current_user_email(token: str = Depends(oauth2)) -> str:
#     try:
#         payload = decode_access_token(token)
#         print("payload decodficicado: ", payload)
#         email: Optional[str] = payload.get("sub")
#         if not email:
#             raise HTTPException(status_code=401, detail="Token inválido (sin sub)")
#         return email
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token expirado")
#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Token inválido")


# ----------------- endpoints -----------------


@router.post("/register",  response_model=ApiKeyPublic)
def register(payload: UserRegister):
    _, users, _ = _get_collections()

    # user_id = uuid.uuid4()
    # print(f"id de user generado en endpoint de register:{user_id}")
    

    if users.find_one({"email": payload.email}):
       
        raise HTTPException(status_code=409, detail="Ese email ya está registrado")

    user_doc = {
        "user_name": payload.user_name,
        "email": payload.email,
        "password": hash_password(payload.password),  # hash
        "createdAt": datetime.now(timezone.utc),
     
    }
    result = users.insert_one(user_doc)

    # Get the inserted user ID as a string
    user_id = str(result.inserted_id)
    print(f"ID de usuario generado en MongoDB (Register) : {user_id}")
    
    # Crear API Key
    
 
    api_key = generate_api_key()
    expires_at = datetime.now() + timedelta(minutes=5)  # Expira en 1 año
    key_data = {
        "key": api_key,
        "user_id": user_id,
        "created_at": datetime.now(),
        "expires_at": expires_at,
        "is_active": True
    }
    api_keys_collection.insert_one(key_data)
    
    print(f"contenido de key data (register): {key_data}")

    # Crear la API key del usuario y retornarla aparte (opcional)
    # Si quieres mostrarla aquí, puedes devolverla en otro campo

    return {
        #Usar el _id de Mongo (como string).
        "username ": payload.user_name,
        "email ": payload.email,
        "password": payload.password,
        #para la APIKEY 
        "api_key": api_key, 
        "expires_at": expires_at
        # "id": str(result.inserted_id),     # devolvemos el id como string
        # "user_id" : str(payload["_id"])
    }


# def find_user_existing(user) -> str:
#     _, users, _ = _get_collections()
#     user = users
#     return user


@router.post("/login", response_model=ApiKeyPublic)
def login(payload: UserLogin):
    print("has ingresado al endpoint de login")
    _, users, _ = _get_collections()
    # user_id = "default_user_id"
    user = users.find_one({"email": payload.email})
    print(f"email encontrado para  el login: {payload.email}")
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    user_id = str(user["_id"])   # ← obtenemos el id real como string
    print(f"id de usuario by mongo (Login): {user_id}")
    
        # Obtener o crear API Key
    key_data = api_keys_collection.find_one({"user_id": user["_id"], "is_active": True})
    if not key_data or key_data["expires_at"] < datetime.now():
        # Crear nueva si no hay o está expirada
        api_key = generate_api_key()
        expires_at = datetime.now() + timedelta(minutes=5)
        key_data = {
            "key": api_key,
            "user_id": user["_id"],
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "is_active": True
        }
        api_keys_collection.update_one(
            {"user_id": user["_id"], "is_active": True},
            {"$set": {"is_active": False}},  # Desactiva keys antiguas
            upsert=False
        )
        api_keys_collection.insert_one(key_data)
        
        print(f"contenido de key data (login): {key_data}")
    else:
        api_key = key_data["key"]
        expires_at = key_data["expires_at"]
        
    
    token = create_access_token(
        # id_user=user_id,
        # user_name=str(user["user_name"]),
        user_id = user_id,
        email=str(user["email"]),
        # days=3,
    )
    # user = users.find_one({"user_name": payload.user_name})

    

    print(f"token imprimido: {token}")
    decode_token = decode_access_token(token)
    print(f"token descomprimido: {decode_token}")
    
    return {"access_token": token, "token_type": "bearer",
            #para la API  KEY
            "api_key": api_key,
            "expires_at": expires_at}


# @router.post("/apikey/rotate", response_model=ApiKeyPublic)
# def rotate_api_key(current_email: str = Depends(get_current_user_email)):
#     """
#     Crea una nueva API key para el usuario autenticado.
#     Devuelve el valor PLANO de la nueva key (guarda el hash en DB).
#     """
#     new_plain_key = _create_and_store_apikey_for(current_email)
#     return ApiKeyPublic(api_key=new_plain_key)


# @router.get("/apikey/exists")
# def has_api_key(current_email: str = Depends(get_current_user_email)):
#     """
#     Retorna si el usuario tiene una API key (no devuelve el valor).
#     """
#     _, _, apikeys = _get_collections()
#     exists = apikeys.find_one({"user_email": current_email}) is not None
#     return {"has_api_key": exists}
