from fastapi import FastAPI
from src.routes.chat import router as chat_router
from src.routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from src.utils.file import indexar_markdowns
from src.utils.mongo_db.create import ensure_indexes

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


# Asegura índices (TTL de 2 horas; cámbialo como quieras)
ensure_indexes(ttl_seconds=7200)

characters = "abcdefghijklmnopqrstuvxywzABCDEFGHIJKLMNOPQRSTUVWYWZ"
# Ejecutar la indexación de los markdowns al arrancar
indexar_markdowns()
# for i in len(list):
    
app.include_router(auth_router)
app.include_router(chat_router)
