from pymongo import MongoClient
from src.config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME, DEFAULT_USERNAME, DEFAULT_PASSWORD, JWT_SECRET_KEY
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

class MongoDBConnection:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.collection = self.db[MONGO_COLLECTION_NAME]
        self.secret_key = JWT_SECRET_KEY

    def get_client(self):
        return self.client

    def close(self):
        self.client.close()

    def find_user(self, username: str, password: str):
        return self.collection.find_one({"username": username, "password": password})

    def insert_user(self, username: str, password: str):
        if self.collection.find_one({"username": username}):
            return False
        self.collection.insert_one({"username": username, "password": password})
        return True

    def verify_default_user(self, username: str, password: str):
        return username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD

    def generate_token(self, username: str):
        payload = {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expirado")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token inválido")

mongo_db = MongoDBConnection()