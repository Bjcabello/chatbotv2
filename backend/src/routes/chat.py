from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from src.config import CHROMA_COLLECTION_PDF, CHROMA_COLLECTION_MD
from src.models.chat import Chat
from src.utils.file import leer_pdf
from src.utils.chroma import indexar_documento
from pathlib import Path
import shutil
import os
from sentence_transformers import SentenceTransformer, util
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
            indexar_documento(nombre=nombre_archivo, contenido=texto, collection_name=CHROMA_COLLECTION_PDF)
    except Exception as error:
        print(f" Error al procesar {nombre_archivo}: {error}")
    finally:
        # Eliminar el archivo temporal
        if os.path.exists(ruta):
            os.remove(ruta)


# Cargamos un modelo de embeddings ligero para clasificación
classifier_model = SentenceTransformer("all-MiniLM-L6-v2")


pdf_examples = [
    "¿Qué dice el documento?",
    "Explícame el archivo que subí",
    "Según el PDF que envié",
    "Resume la página 2 del documento",
    "Analiza el texto del archivo",
    "pdf",
    "explicame",
    "archivo",
    "pdf",
    "quiere decir",
    "documento",
    "papel",
    "dime",
    "entender",
    "que",
    "como",
    "cuantos",
    "cuanto",
    "donde",
    "quien"
    "quienes"
]

md_examples = [
    "¿Cuál es la lógica de negocio?",
    "¿Qué restricciones hay?",
    "Describe la personalidad del sistema",
    "Explica las reglas del sistema",
    "Contexto base",
    "eliminar",
    "como creo un usuario?",
    "como edito un usuario?",
    "como borro un usuario?",
    "como se dice perro en ingles",
    "crear",
    "editar",
    "viamatica",
    "instrucciones"
    "gracias"
    "adios"
    "como te llamas?"
]

def detectar_tipo_pregunta(pregunta: str) -> str:
    embedding_pregunta = classifier_model.encode(pregunta, convert_to_tensor=True)

    # Similaridad con ejemplos PDF
    embedding_pdf = classifier_model.encode(pdf_examples, convert_to_tensor=True)
    score_pdf = util.cos_sim(embedding_pregunta, embedding_pdf).max().item()

    # Similaridad con ejemplos Markdown
    embedding_md = classifier_model.encode(md_examples, convert_to_tensor=True)
    score_md = util.cos_sim(embedding_pregunta, embedding_md).max().item()

    print(f"📊 Similitud PDF: {score_pdf:.4f} | Markdown: {score_md:.4f}")

    return CHROMA_COLLECTION_PDF if score_pdf > score_md else CHROMA_COLLECTION_MD

@router.post("/chat")
def chat(data: Chat):
    try:
        from langchain_ollama import OllamaLLM
        from langchain.chains.retrieval_qa.base import RetrievalQA
        from langchain.prompts import PromptTemplate

        llm = OllamaLLM(model="mistral", temperature=0.1)

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
        
        print(respuesta_completa)

        return solo_respuesta

    except Exception as e:
        return {"error": str(e)}
