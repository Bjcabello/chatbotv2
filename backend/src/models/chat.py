from pydantic import BaseModel, Field
from typing import Literal
import uuid

class Chat(BaseModel):
    pregunta: str
    context_type: Literal['Documentos', 'Procesos'] = 'Documentos'
    id_document: str = Field(default_factory=lambda: str(uuid.uuid4()))
