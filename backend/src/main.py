from fastapi import FastAPI
from src.routes.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.title = "ChatBot IA"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)