from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.models.chat import Chat
from src.utils.file import leer_markdown, leer_pdf,store_pdf_text
from src.services.chatbot import construir_prompt, enviar_a_ollama
from src.config import BASE_CONTEXT, PROCESSES_CONTEXT
from src.utils.processes import detectar_proceso
from src.utils.chroma import buscar_fragmentos_relevantes
from pathlib import Path
import shutil
import uuid

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/pdf/upload")
def upload_pdf(file: bytes):
    temp_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
        
    text_extracted = leer_pdf(temp_path)
    store_pdf_text(text_extracted, doc_name=file.filename)
    

@router.post("/chat")
def chat(data: Chat):
    personalidad = leer_markdown(BASE_CONTEXT / "personality.md")
    logica = leer_markdown(BASE_CONTEXT / "business_logic.md")
    restriccion = leer_markdown(BASE_CONTEXT / "restrictions.md")
    

    nombre_proceso, contenido_proceso = detectar_proceso(data.pregunta, PROCESSES_CONTEXT)
    fragmentos = buscar_fragmentos_relevantes(data.pregunta)

    prompt = construir_prompt(
        data.usuario,
        data.dni,
        data.tipo_usuario,
        data.pregunta,
        personalidad,
        logica,
        contenido_proceso + "\n\n" + fragmentos,
        restriccion
    )

    return StreamingResponse(
        enviar_a_ollama(prompt),
        media_type="text/plain"
    )
