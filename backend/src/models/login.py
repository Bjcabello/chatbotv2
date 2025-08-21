from pydantic import BaseModel, Field, EmailStr
import uuid
from datetime import datetime


class AuthRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico válido (requerido)")
    password: str = Field(..., min_length=6, description="Contraseña con al menos 6 caracteres")

    class Config:
        json_schema_extra = {}

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico válido (requerido)")
    password: str = Field(..., min_length=6, description="Contraseña con al menos 6 caracteres")

    class Config:
        json_schema_extra = {}


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Token JWT para autenticación")
    token_type: str = Field(default="bearer", description="Tipo de token")
    user_id: uuid.UUID = Field(..., description="ID único del usuario")

    class Config:
        json_schema_extra = {}


class UserInDB(BaseModel):
    user_id: uuid.UUID = Field(..., description="ID único del usuario")
    email: EmailStr = Field(..., description="Correo electrónico válido")
    password: str = Field(..., description="Contraseña hasheada")
    created_at: datetime = Field(..., description="Fecha de creación")

    class Config:
        json_schema_extra = {}
        