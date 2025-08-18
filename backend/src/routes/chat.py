from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from src.models.chat import Chat
from fastapi import APIRouter, HTTPException, Depends, status
from src.models.login import AuthRequest, LoginRequest
from src.db.mongodb import mongo_db
from fastapi.security import OAuth2PasswordBearer
from src.utils.file import leer_pdf, indexar_markdowns, leer_markdown
from src.utils.chroma import indexar_documento, buscar_fragmentos_relevantes, get_chroma_vectorstore
from src.config import CHROMA_MARKDOWN_COLLECTION, CHROMA_PDF_COLLECTION
from pathlib import Path
import shutil
import os
import time

router = APIRouter()


indexar_markdowns()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    email = mongo_db.verify_token(token)
    return email

@router.post("/register")
def register(registration_request: AuthRequest):
    try:
        if mongo_db.insert_user(registration_request.email, registration_request.password):
            update_data = {"email": registration_request.email, "password": registration_request.password}
            update_data["user_id"] = registration_request.user_id
            mongo_db.collection.update_one(
                {"email": registration_request.email},
                {"$set": update_data},
                upsert=True
            )
            return {"message": f"Registro exitoso para {registration_request.email}.", "status": "success"}
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    except HTTPException as e:
        raise e
    except Exception as e:
        return {"error": str(e)}

@router.post("/login")
def login(login_request: LoginRequest):
    try:
        if mongo_db.verify_default_user(login_request.email, login_request.password):
            token = mongo_db.generate_token(login_request.email)
            return {"message": f"Inicio sesión exitoso {login_request.email}.", "token": token, "status": "success"}
        user = mongo_db.find_user(login_request.email, login_request.password)
        if user:
            token = mongo_db.generate_token(login_request.email)
            return {"message": f"Inicio sesión exitoso {login_request.email}. ", "token": token, "status": "success"}
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException as e:
        raise e
    except Exception as e:
        return {"error": str(e)}


@router.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    try:
        ruta_temporal = f"./temp_{file.filename}"
        with open(ruta_temporal, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        background_tasks.add_task(procesar_pdf_en_background, ruta_temporal, file.filename)

        return {"mensaje": f"{file.filename} subido con éxito. 😊"}
    except Exception as e:
        return {"error": str(e)}

def procesar_pdf_en_background(ruta: str, nombre_archivo: str):
    try:
        texto = leer_pdf(ruta)
        print(f"Texto extraído del PDF {nombre_archivo}: {texto[:200]}...")  # Depuración
        if texto.strip():
            indexar_documento(nombre=nombre_archivo, contenido=texto, collection_name=CHROMA_PDF_COLLECTION, categoria="pdf")
    except Exception as error:
        print(f"❌ Error al procesar {nombre_archivo}: {error}")
    finally:
        if os.path.exists(ruta):
            os.remove(ruta)

@router.post("/chat")
def chat(data: Chat):
    try:
        from langchain_ollama import OllamaLLM
        from langchain.chains.retrieval_qa.base import RetrievalQA
        from langchain.prompts import PromptTemplate

        start_time = time.time()
        llm = OllamaLLM(model="gemma:2b", temperature=0)  # Cambiado a tinyllama (más ligero)

        # Recuperar contexto base (personalidad, lógica, restricciones)
        contexto_base = "\n".join(buscar_fragmentos_relevantes("contexto general", CHROMA_MARKDOWN_COLLECTION, category_filter="base", n_results=3))
        print(f"Contexto base: {contexto_base[:200]}...")  # Depuración

        # Detectar si la pregunta está relacionada con un proceso
        pregunta = data.pregunta.lower()
        proceso_relevante = None
        procesos = ["create_user", "update_user", "remove_user"]
        for proceso in procesos:
            if proceso in pregunta:
                proceso_relevante = proceso
                break

        # Recuperar contexto del proceso si aplica
        contexto_proceso = ""
        if proceso_relevante:
            contexto_proceso = "\n".join(buscar_fragmentos_relevantes(f"proceso {proceso_relevante}", CHROMA_MARKDOWN_COLLECTION, category_filter="processes", n_results=3))
            print(f"Contexto proceso: {contexto_proceso[:200]}...")  # Depuración

        # Recuperar contexto del PDF con detección genérica
        contexto_pdf = ""
        if any(phrase in pregunta for phrase in ["en el pdf", "sobre el documento", "en el documento", "del pdf"]):
            pdf_content = buscar_fragmentos_relevantes(pregunta, CHROMA_PDF_COLLECTION, category_filter="pdf", n_results=5)
            contexto_pdf = "\n".join(pdf_content)
            print(f"Contexto PDF: {contexto_pdf[:200]}...") 

        # Combinar contextos
        contexto_total = contexto_pdf if contexto_pdf else f"{contexto_base}\n\n{contexto_proceso}".strip()
        if not contexto_total:
            contexto_total = contexto_base
        print(f"Contexto total: {contexto_total[:200]}...") 

        # Configurar el prompt
        prompt = PromptTemplate(
            template="""  
                Contexto:
                {context}
                
                Pregunta:
                {question}
                
                Respuesta: (Inicia con 'Estimado(a),' y usa un tono amable y profesional)
            """, input_variables=["context", "question"]
        )

        retriever = get_chroma_vectorstore(CHROMA_PDF_COLLECTION if contexto_pdf else CHROMA_MARKDOWN_COLLECTION).as_retriever(search_kwargs={"k": 5})
        retrieval = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )

        respuesta_completa = retrieval.invoke({"query": data.pregunta, "context": contexto_total})
        solo_respuesta = respuesta_completa["result"]
        print(f"Respuesta generada: {solo_respuesta[:200]}...")  

        # Verificar si la respuesta es adecuada
        if "Lo siento" in solo_respuesta or "no contiene información suficiente" in solo_respuesta:
            return solo_respuesta
        elif not solo_respuesta.strip():
            return "Estimado(a), el documento proporcionado no contiene información suficiente sobre esa pregunta. 😔"

        return solo_respuesta

    except Exception as e:
        print(f"Error en chat: {str(e)}")  
        return {"error": str(e)}