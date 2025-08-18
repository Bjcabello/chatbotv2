# src/db/mongodb.py
from pymongo import MongoClient
from src.config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME, DEFAULT_USERNAME, DEFAULT_PASSWORD, JWT_SECRET_KEY
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

class MongoDBConnection:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        try:
            self.client.admin.command('ping')
            self.db = self.client[MONGO_DB_NAME]
            self.collection = self.db[MONGO_COLLECTION_NAME]
            self.secret_key = JWT_SECRET_KEY
            print("Conexión a MongoDB exitosa")
        except Exception as e:
            print(f"Error de conexión a MongoDB: {e}")
            raise

    def __del__(self):
        self.close()

    def get_client(self):
        return self.client

    def close(self):
        self.client.close()

    def find_user(self, email: str, password: str):
        if not email or not password:
            return None
        return self.collection.find_one({"email": email, "password": password})

    def insert_user(self, email: str, password: str):
        if not email or not password:
            return False
        if self.collection.find_one({"email": email}):
            return False
        self.collection.insert_one({"email": email, "password": password})
        return True

    def verify_default_user(self, email: str, password: str):
        return email == DEFAULT_USERNAME and password == DEFAULT_PASSWORD

    def generate_token(self, email: str):
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        payload = {
            "sub": email,
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
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