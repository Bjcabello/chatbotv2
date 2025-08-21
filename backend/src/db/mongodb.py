from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from src.config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME, DEFAULT_USERNAME, DEFAULT_PASSWORD, JWT_SECRET_KEY
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import uuid
# No necesitamos importar UuidRepresentation si usamos la cadena 'standard'

class MongoDBConnection:
    def __init__(self):
        try:
            print(f"Intentando conectar a MONGO_URI: {MONGO_URI}")
            print(f"DB Name: {MONGO_DB_NAME}, Collection: {MONGO_COLLECTION_NAME}")
            # Usa 'standard' como cadena en lugar de UuidRepresentation.STANDARD
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, uuidRepresentation='standard')
            print("Ping a MongoDB...")
            self.client.admin.command('ping')
            self.db = self.client[MONGO_DB_NAME]
            self.collection = self.db[MONGO_COLLECTION_NAME]
            print("Creando índice...")
            self.collection.create_index("email", unique=True)
            self.secret_key = JWT_SECRET_KEY
            print("Conexión a MongoDB exitosa. JWT_SECRET_KEY cargado:", self.secret_key[:10] + "..." if self.secret_key else "None")
        except ServerSelectionTimeoutError as e:
            print(f"Error de conexión a MongoDB: {e}")
            raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
        except Exception as e:
            print(f"Error inesperado durante inicialización: {e}")
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    def __del__(self):
        # Maneja el caso en que self.client no esté definido
        if hasattr(self, 'client') and self.client:
            self.close()

    def close(self):
        if self.client:
            self.client.close()
            print("Conexión a MongoDB cerrada.")

    def get_client(self):
        return self.client

    def find_user(self, email: str, password: str):
        if not email or not password:
            return None
        return self.collection.find_one({"email": email, "password": password})

    def insert_user(self, user_id: uuid.UUID, email: str, password: str, created_at: datetime):
        if not email or not password or not user_id:
            return False
        try:
            print(f"Intentando insertar usuario - user_id: {user_id}, email: {email}, created_at: {created_at}")
            result = self.collection.insert_one({
                "user_id": user_id,
                "email": email,
                "password": password,
                "created_at": created_at
            })
            print(f"Usuario insertado con _id: {result.inserted_id}")
            return True
        except Exception as e:
            print(f"Error al insertar usuario: {str(e)}")
            if "duplicate key error" in str(e).lower():
                return False
            raise HTTPException(status_code=500, detail=f"Error al insertar usuario: {str(e)}")

    def verify_default_user(self, email: str, password: str):
        return email == DEFAULT_USERNAME and password == DEFAULT_PASSWORD

    def generate_token(self, user_id: str):
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        payload = {
            "sub": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str):
        try:
            if not token:
                raise HTTPException(status_code=401, detail="Token is required")
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expirado")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token inválido")

mongo_db = MongoDBConnection()