from pydantic import BaseModel, Field, EmailStr
import uuid

class AuthRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico válido (requerido)")
    password: str = Field(..., min_length=6, description="Contraseña con al menos 6 caracteres")
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Identificador único del usuario", exclude=True)

    class Config:
        json_schema_extra = {}  


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico válido (requerido)")
    password: str = Field(..., min_length=6, description="Contraseña con al menos 6 caracteres")