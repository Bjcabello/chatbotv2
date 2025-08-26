from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from src.config import CHROMA_COLLECTION_PDF, CHROMA_COLLECTION_MD
from src.models.chats_models import Chat
from src.utils.file import leer_pdf
from src.utils.chroma import indexar_documento
from pathlib import Path
import shutil
import os
from src.utils.filtered_responses import detectar_tipo_pregunta
from src.conteo_token import count_tokens

router = APIRouter()

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
            # Conteo de tokens por subida de PDF
            pdf_tokens = count_tokens(texto)
            print(f"Tokens generados por la subida del PDF '{nombre_archivo}': {pdf_tokens}")
            indexar_documento(nombre=nombre_archivo, contenido=texto, collection_name=CHROMA_COLLECTION_PDF)
    except Exception as error:
        print(f" Error al procesar {nombre_archivo}: {error}")
    finally:
        # Eliminar el archivo temporal
        if os.path.exists(ruta):
            os.remove(ruta)

@router.post("/chat")
def chat(data: Chat):
    try:
        from langchain_ollama import OllamaLLM
        from langchain.chains.retrieval_qa.base import RetrievalQA
        from langchain.prompts import PromptTemplate

        llm = OllamaLLM(model="mistral", temperature=0.1)
        # llm = OllamaLLM(model="gemma:2b ", temperature=0.1)
        #  Aquí decides la colección según la pregunta
        #  Usamos la detección semántica
        collection_name = detectar_tipo_pregunta(data.pregunta)

        from src.utils.chroma import get_chroma_vectorstore
        retriever = get_chroma_vectorstore(collection_name).as_retriever(search_kwargs={"k": 5})

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
        
        # --- Nuevos conteos de tokens ---
        # Tokens de la pregunta del usuario
        question_tokens = count_tokens(data.pregunta)
        print(f"Tokens generados por la pregunta del usuario: {question_tokens}")
        
        # Contexto recuperado de Chroma (source_documents)
        context_docs = respuesta_completa.get("source_documents", [])
        context_text = "\n\n".join([doc.page_content for doc in context_docs])
        context_tokens = count_tokens(context_text)
        print(f"Tokens en el contexto recuperado: {context_tokens}")
        
        # Prompt completo aproximado (input a Ollama)
        prompt_text = prompt.template.format(context=context_text, question=data.pregunta)
        input_tokens = count_tokens(prompt_text)
        print(f"Tokens totales en el prompt input (contexto + pregunta): {input_tokens}")
        
        # Tokens de la respuesta del chatbot
        response_tokens = count_tokens(solo_respuesta)
        print(f"Tokens generados por la respuesta del chatbot: {response_tokens}")
        
        print(respuesta_completa)

        return solo_respuesta

    except Exception as e:
        return {"error": str(e)}
