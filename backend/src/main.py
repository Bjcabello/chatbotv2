from fastapi import FastAPI
from src.routes.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware
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

characters = "abcdefghijklmnopqrstuvxywzABCDEFGHIJKLMNOPQRSTUVWYWZ"

# for i in len(list):
    

app.include_router(chat_router)
