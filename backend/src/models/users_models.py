#backend/src/models/users_models.py
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class User(BaseModel):
    id: UUID  # UUID para el ID
    user_name: str
    password: str  # En producción, esto sería un hash
    email: EmailStr  # Validación de email con pydantic


class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Lo que guardas en DB (opcional si quieres serializar)
class UserInDB(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_name: str
    email: EmailStr
    password: str  # aquí guardamos el HASH
    createdAt: datetime

# Lo que devuelves al cliente (sin password)
class UserPublic(BaseModel):
    user_name: str
    email: EmailStr


# Ejemplo de validación
# def validate_user_data(user: User):
#     return {
#         "_id": user.id.bytes,
#         "user_name": user.user_name,
#         "password": user.password,
#         "email": user.email
#     }