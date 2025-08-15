from pydantic import BaseModel, EmailStr, TypedDict
from uuid import UUID

class User(TypedDict):
    id: UUID  # UUID para el ID
    user_name: str
    password: str  # En producción, esto sería un hash
    email: EmailStr  # Validación de email con pydantic

# Ejemplo de validación
# def validate_user_data(user: User):
#     return {
#         "_id": user.id.bytes,
#         "user_name": user.user_name,
#         "password": user.password,
#         "email": user.email
#     }