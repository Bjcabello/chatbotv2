from fastapi import FastAPI
from src.routes.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware
from src.utils.file import indexar_markdowns
import random

app = FastAPI()
app.title = "ChatBot IA"
print(app.title)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ejecutar la indexación de los markdowns al arrancar
indexar_markdowns()

app.include_router(chat_router, prefix="/api")

