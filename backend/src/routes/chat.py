from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from src.models.chat import Chat
from src.utils.file import leer_markdown, leer_pdf, detectar_proceso
from src.services.chatbot import construir_prompt, enviar_a_ollama
from src.config import BASE_CONTEXT, PROCESSES_CONTEXT
from src.utils.chroma import buscar_fragmentos_relevantes, indexar_documento
from pathlib import Path
import shutil
import uuid
import shutil
import os
import requests

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/gutenberg")
def subir_libros_gutenberg(inicio: int = 100, fin: int = 200):
    resultados = []
    for libro_id in range(inicio, fin + 1):
        url = f"https://www.gutenberg.org/files/{libro_id}/{libro_id}-pdf.pdf"
        print(f" Descargando: {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            nombre_archivo = f"libro_{libro_id}.pdf"
            with open(nombre_archivo, "wb") as f:
                f.write(response.content)

            try:
                texto = leer_pdf(nombre_archivo)
                if texto.strip():
                    indexar_documento(nombre=f"Libro-{libro_id}", contenido=texto)
                    resultados.append(f" Libro {libro_id} indexado.")
                else:
                    resultados.append(f" Libro {libro_id} no tiene texto válido.")
            except Exception as e:
                resultados.append(f" Error procesando {libro_id}: {str(e)}")
            finally:
                os.remove(nombre_archivo)
        else:
            resultados.append(f" No encontrado (404): {url}")
    
    return {"resultado": resultados}

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
        contenido_proceso + "\n\n" + "\n".join(fragmentos),
        restriccion
    )

    return StreamingResponse(
        enviar_a_ollama(prompt),
        media_type="text/plain"
    )