from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from src.models.chat import Chat
from fastapi import APIRouter, HTTPException, Depends, status
from src.models.login import AuthRequest, LoginRequest, TokenResponse
from pydantic import BaseModel
from src.db.mongodb import mongo_db
from fastapi.security import OAuth2PasswordBearer
from src.utils.file import leer_pdf, indexar_markdowns, leer_markdown, indexar_pdf
from langchain_ollama import OllamaLLM
from langchain.chains.retrieval_qa.base import RetrievalQA
from fastapi.responses import StreamingResponse
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from src.utils.chroma import indexar_documento, buscar_fragmentos_relevantes, get_chroma_vectorstore
from src.config import CHROMA_MARKDOWN_COLLECTION, CHROMA_PDF_COLLECTION
from pathlib import Path
import shutil
import os
import uuid
import time
from fastapi import Depends
from datetime import datetime, timezone

router = APIRouter()

indexar_markdowns()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user_id = mongo_db.verify_token(token)
        return user_id
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.post("/register", response_model=TokenResponse)
def register(registration_request: AuthRequest):
    try:
        print(f"Registrando usuario: {registration_request.email}")
        created_at = datetime.now(timezone.utc)
        user_id = uuid.uuid4()
        print(f"Generado user_id: {user_id}")
        if mongo_db.insert_user(user_id, registration_request.email, registration_request.password, created_at):
            print("Usuario insertado exitosamente")
            token = mongo_db.generate_token(str(user_id))
            print(f"Token generado: {token[:20]}...")
            return {"access_token": token, "token_type": "bearer", "user_id": user_id}
        raise HTTPException(status_code=409, detail="El email ya está registrado")
    except HTTPException as e:
        print(f"HTTPException en /register: {str(e)}")
        raise e
    except Exception as e:
        print(f"Error inesperado en /register: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    
@router.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest):
    try:
        if mongo_db.verify_default_user(login_request.email, login_request.password):
            user_id = "default_user_id"
            token = mongo_db.generate_token(user_id)
            return {"access_token": token, "token_type": "bearer", "user_id": uuid.UUID(user_id)}
        user = mongo_db.find_user(login_request.email, login_request.password)
        if user:
            token = mongo_db.generate_token(str(user["user_id"]))
            return {"access_token": token, "token_type": "bearer", "user_id": user["user_id"]}
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    try:
        ruta_temporal = f"./temp_{file.filename}"
        with open(ruta_temporal, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        background_tasks.add_task(procesar_pdf_en_background, ruta_temporal, file.filename)

        return {"mensaje": f"{file.filename} subido con éxito. "}
    except Exception as e:
        return {"error": str(e)}

def procesar_pdf_en_background(ruta: str, nombre_archivo: str):
    try:
        texto = leer_pdf(Path(ruta))
        print(f"Texto extraído del PDF {nombre_archivo}: {texto[:200]}...")  
        if texto.strip():
            indexar_pdf(nombre=nombre_archivo, contenido=texto)
    except Exception as error:
        print(f"❌ Error al procesar {nombre_archivo}: {error}")
    finally:
        if os.path.exists(ruta):
            os.remove(ruta)

@router.post("/chat")
def chat_stream(data: Chat):
    try:
        start_time = time.time()

        # Inicializar LLM con streaming activado
        llm = ChatOllama(model="mistral", temperature=0, streaming=True)

        pregunta = data.pregunta.lower()
        contexto_total = ""

        # --- Recuperar contexto según el tipo ---
        if data.context_type == "Documentos":
            pdf_content = buscar_fragmentos_relevantes(
                pregunta, CHROMA_PDF_COLLECTION, category_filter="pdf", n_results=5
            )
            contexto_total = "\n".join(pdf_content)
            print(f" Contexto Documentos: {contexto_total[:200]}...")
            if not contexto_total:
                print(" Advertencia: No se encontraron fragmentos relevantes en los Documentos")

        elif data.context_type == "Procesos":
            proceso_relevante = None
            procesos = ["create_user", "update_user", "remove_user"]
            for proceso in procesos:
                if proceso in pregunta:
                    proceso_relevante = proceso
                    break
            if proceso_relevante:
                contexto_total = "\n".join(
                    buscar_fragmentos_relevantes(
                        f"proceso {proceso_relevante}", 
                        CHROMA_MARKDOWN_COLLECTION, 
                        category_filter="processes", 
                        n_results=3
                    )
                )
            else:
                contexto_total = "No se detectó un proceso relevante."
            print(f" Contexto Procesos: {contexto_total[:200]}...")

        else:
            raise HTTPException(status_code=400, detail="Tipo de contexto no válido. Use 'Documentos' o 'Procesos'")

        print(f" Contexto total: {contexto_total[:200]}...")

        # --- Construir el prompt ---
        prompt = f"""
        Contexto:
        {contexto_total}

        Pregunta:
        {data.pregunta}

        Respuesta: (Inicia con 'Estimado(a),' y usa un tono amable y profesional)
        """

        # --- Generar la respuesta en streaming ---
        def generate():
            for chunk in llm.stream(prompt):
                if chunk.content:
                    yield chunk.content  # Devuelve token por token

        return StreamingResponse(generate(), media_type="text/plain")

    except Exception as e:
        print(f"Error en chat: {str(e)}")
        return {"error": str(e)}