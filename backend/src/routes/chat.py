from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
from src.models.chat import Chat
from src.utils.file import leer_markdown, leer_pdf
from src.services.chatbot import construir_prompt, enviar_a_ollama
from src.config import BASE_CONTEXT, PROCESSES_CONTEXT
from src.utils.processes import detectar_proceso
from src.utils.chroma import buscar_fragmentos_relevantes, indexar_documento
from pathlib import Path
import shutil
import uuid
import shutil
import os

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    try:
        # Ruta temporal para guardar el archivo
        ruta_temporal = f"./temp_{file.filename}"
        
        print("")

        # Guardar el archivo en disco
        with open(ruta_temporal, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Procesar el archivo PDF en segundo plano
        background_tasks.add_task(procesar_pdf_en_background, ruta_temporal, file.filename)

        return {"mensaje": f"{file.filename} subido con éxito. "}
    
    except Exception as e:
        return {"error": str(e)}

def procesar_pdf_en_background(ruta: str, nombre_archivo: str):
    try:
        texto = leer_pdf(ruta)
        if texto.strip():
            indexar_documento(nombre=nombre_archivo, contenido=texto)
    except Exception as error:
        print(f"❌ Error al procesar {nombre_archivo}: {error}")
    finally:
        # Eliminar el archivo temporal
        if os.path.exists(ruta):
            os.remove(ruta)


@router.post("/chat")
def chat(data: Chat):
    try:
        # Leer contexto base desde los markdown
        # personalidad = leer_markdown(BASE_CONTEXT / "personality.md")
        # logica = leer_markdown(BASE_CONTEXT / "business_logic.md")
        # restriccion = leer_markdown(BASE_CONTEXT / "restrictions.md")
        # contexto_base = f"{personalidad}\n\n{logica}\n\n{restriccion}"

        from langchain_ollama import OllamaLLM

        llm = OllamaLLM(model="mistral", temperature=0)


        from src.utils.chroma import get_chroma_vectorstore
        retriever = get_chroma_vectorstore().as_retriever(search_kwargs={"k": 5})

        from langchain.chains.retrieval_qa.base import RetrievalQA
        from langchain.prompts import PromptTemplate

        prompt = PromptTemplate(
            template="""  
                Contexto:
                {context}
                
                Pregunta:
                {question}
                
                Respuesta:
            """, input_variables=["context", "question"]
        )

        retrieval = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )

        # pregunta_final = f"{contexto_base}\n\n{data.pregunta}"
        # result = retrieval.invoke({"query": pregunta_final})

        # return result
        respuesta_completa = retrieval.invoke({"query": data.pregunta})
        solo_respuesta = respuesta_completa["result"]

        return {"respuesta": solo_respuesta}

    except Exception as e:
        return {"error": str(e)}
