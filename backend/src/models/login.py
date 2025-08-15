# src/models/login.py
from pydantic import BaseModel, Field, EmailStr
import uuid

class AuthRequest(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Identificador único del usuario")
    username: str = Field(min_length=3, description="Nombre de usuario con al menos 3 caracteres")
    password: str = Field(min_length=6, description="Contraseña con al menos 6 caracteres")
    mail: EmailStr = Field(..., description="Correo electrónico válido")