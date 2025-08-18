from pydantic import BaseModel, Field
from typing import Literal

class Chat(BaseModel):
    pregunta: str

