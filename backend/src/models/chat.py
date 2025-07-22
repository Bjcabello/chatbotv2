from pydantic import BaseModel, Field

class Chat(BaseModel):
    usuario: str
    dni: str = Field(min_length=10, max_length=10)
    tipo_usuario: str
    pregunta: str
