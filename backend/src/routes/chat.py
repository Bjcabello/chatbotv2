from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from src.models.chat import Chat
from src.utils.file import leer_markdown, leer_pdf
from src.services.chatbot import construir_prompt, enviar_a_ollama
from src.config import BASE_CONTEXT, PROCESSES_CONTEXT
from src.utils.processes import detectar_proceso
from src.utils.chroma import indexar_documento, buscar_en_pdfs
from pathlib import Path
import shutil
import uuid
import shutil
import os

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def responder_usuario(pregunta_usuario: str) -> str:
    # Puedes usar aquí alguna heurística para detectar si la pregunta es sobre un PDF
    # Por ahora asumimos que TODA pregunta busca en los PDFs
    fragmentos = buscar_en_pdfs(pregunta_usuario)
    
    if not fragmentos:
        return "No encontré información relevante en los documentos PDF cargados."
    
    respuesta_contexto = "\n\n".join(fragmentos)
    return f"Basado en los documentos cargados, encontré lo siguiente:\n\n{respuesta_contexto}"


@router.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...)):
    try:
        # Guardar el archivo temporalmente
        ruta_temp = f"./temp_{file.filename}"
        with open(ruta_temp, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Leer contenido del PDF
        texto = leer_pdf(ruta_temp)
        if not texto.strip():
            os.remove(ruta_temp)
            return {"error": "El PDF no contiene texto válido."}

        # Indexar en ChromaDB
        nombre = file.filename
        indexar_documento(nombre=nombre, contenido=texto)

        # Eliminar archivo temporal
        os.remove(ruta_temp)

        return {"mensaje": f"{file.filename} subido e indexado correctamente"}

    except Exception as e:
        return {"error": str(e)}

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
