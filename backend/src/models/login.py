# src/models/login.py
from pydantic import BaseModel, Field

class AuthRequest(BaseModel):
    username: str = Field(..., min_length=3, description="Nombre de usuario con al menos 3 caracteres")
    password: str = Field(..., min_length=6, description="Contraseña con al menos 6 caracteres")

    class Config:
        schema_extra = {
            "example": {
                "username": "bryan",
                "password": "securepass"
            }
        }