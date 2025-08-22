# backend/src/models/users_models.py
from pydantic import BaseModel, EmailStr, Field
import uuid 
from datetime import datetime
from typing import Optional


class UserRegister(BaseModel):  # lo que envía el cliente al registrarse
    # id:  uuid.UUID # UUID para el ID
    user_name: str
    password: str 
    email: EmailStr  # Validación de email con pydantic


class UserLogin(BaseModel):  # lo que envía el cliente al hacer login
    # id: uuid.UUID
    # user_name: str
    email: EmailStr
    password: str


# Lo que devuelves al cliente (sin password)
# class UserPublic(BaseModel):  # lo que devuelves al registrar (sin password)
#     email: EmailStr


class ApiKeyPublic(BaseModel):  # lo que devuelves al rotar/crear API key
    api_key: str  # se muestra solo al crearse/rotarse4
    #tiempo que expira
