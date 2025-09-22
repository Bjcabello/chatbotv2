from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from src.config import CHROMA_COLLECTION_PDF, CHROMA_COLLECTION_MD,CHROMA_PDF_COLLECTION, CHROMA_MARKDOWN_COLLECTION
from src.models.chats_models import Chat
from src.utils.file import leer_pdf, indexar_pdf
from src.utils.chroma import indexar_documento, buscar_fragmentos_relevantes
from pathlib import Path
import shutil
import os
from src.conteo_token import count_tokens
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, HTTPException, Depends, status
from langchain_ollama import ChatOllama
from src.routes.auth_routes import get_current_user

router = APIRouter()

@router.post("/upload-pdf" )
def upload_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    try:
        # Ruta temporal para guardar el archivo
        ruta_temporal = f"./temp_{file.filename}"

        # Guardar el archivo en disco
        with open(ruta_temporal, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            leer_pdf(ruta_temporal)  # si excede límite, lanza excepción
        except Exception as e:
            os.remove(ruta_temporal)  # borrar archivo temporal
            return {"error": str(e)}

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
            # indexar_documento(nombre=nombre_archivo, contenido=texto, collection_name=CHROMA_COLLECTION_PDF)
            if texto.strip():
                indexar_pdf(nombre=nombre_archivo, contenido=texto)
    except Exception as error:
        print(f" Error al procesar {nombre_archivo}: {error}")
    finally:
        # Eliminar el archivo temporal
        if os.path.exists(ruta):
            os.remove(ruta)

@router.post("/chat")
def chat(data: Chat):
    try:
        
        import os
        from dotenv import load_dotenv
        from langchain_openai import ChatOpenAI
        # Cargar variables de entorno desde .env
        load_dotenv()

        # Obtener la clave de OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY no encontrada. Configura la clave en el archivo .env."
            )

        # Inicializar el modelo de OpenAI
        llm = ChatOpenAI(
            openai_api_key=api_key,  # Pasar la clave explícitamente
            model="gpt-3.5-turbo",   # Modelo por defecto
            temperature=0.1,
            streaming=True
        )

        question  = data.pregunta.lower()
        context_full = ""

        # from src.utils.chroma import get_chroma_vectorstore
        # retriever = get_chroma_vectorstore(collection_name).as_retriever(search_kwargs={"k": 5})
        if data.context_type == "Documents":
            pdf_content = buscar_fragmentos_relevantes(
                question, CHROMA_PDF_COLLECTION, category_filter="pdf", n_results=5
            )
            context_full = "\n".join(pdf_content)
            print(f" Contexto Documentos(clave): {context_full}")
            if not context_full:
                print(" Advertencia: No se encontraron fragmentos relevantes en los Documentos")

        elif data.context_type == "Proccess":
            process_content = buscar_fragmentos_relevantes(
                question, CHROMA_MARKDOWN_COLLECTION, category_filter="processes", n_results=5
            )
            
            process_content_base = buscar_fragmentos_relevantes(
                question, CHROMA_MARKDOWN_COLLECTION, category_filter="base", n_results=5
            )

            context_full = "\n".join(process_content +  process_content_base)
            print(f" Contexto Procesos (clave): {context_full}")
            if not process_content and not process_content_base:
                print("No se encontraron fragmentos relevantes en Procesos ni en Base")
            if not context_full:
                print(" Advertencia: No se encontraron fragmentos relevantes en los Documentos")
            

        else:
            raise HTTPException(status_code=400, detail="Tipo de contexto no válido. Use 'Documentos' o 'Procesos'")

        print(f" Contexto total: {context_full}...")
    
        prompt = f"""  
        Contexto:
        {context_full}

        Pregunta:
        {data.pregunta}

        Respuesta: (Inicia con 'Estimado(a),' y usa un tono amable y profesional)

        """
        print(f"--- ---- --- pregunta hecha por el usuario: {data.pregunta}\n")
        question_tokens = count_tokens(data.pregunta)
        print(f"Tokens generados por la pregunta del usuario: {question_tokens}")
        
        response_content = []


        def generate():
            for chunk in llm.stream(prompt):
                if hasattr(chunk, 'content') and chunk.content:
                    response_content.append(chunk.content)  # Acumular fragmento
                    yield chunk.content  
         
        full_response = "".join(response_content)
        print(f"\nRespuesta completa:\n{full_response}")
        response_tokens = count_tokens(full_response)
        print(f"Tokens generados por la respuesta del chatbot: {response_tokens}")           

        la_respuesta = StreamingResponse(generate(), media_type="text/plain")
        print(f"la respuesta : {la_respuesta}")
        return la_respuesta
    

    except Exception as e:
        return {"error": str(e)}
