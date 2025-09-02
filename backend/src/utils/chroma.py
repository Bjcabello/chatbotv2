from langchain_chroma import Chroma
from src.config import EMBEDDING_MODEL_NAME, CHROMA_DB_PATH, CHROMA_MARKDOWN_COLLECTION, CHROMA_PDF_COLLECTION
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.docstore.document import Document
from typing import Optional, List, Dict
import hashlib
import time
import uuid


embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)


def get_chroma_vectorstore(collection_name: str):
    return Chroma(
        collection_name=collection_name,
        embedding_function=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )

def dividir_en_chunks(texto: str, chunk_size=600, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(texto)

def generar_hash(texto: str) -> str:
    if not isinstance(texto, str):
        raise ValueError("El input debe ser un string")
    hash_obj = hashlib.sha256(texto.encode('utf-8'))
    return hash_obj.hexdigest()


def indexar_documento(nombre: str, contenido: str, collection_name: str, categoria: str):
    vectorstore = get_chroma_vectorstore(collection_name)
    
    
    id_document = str(uuid.uuid4())

    
    hash_value = generar_hash(contenido)
    
    find_hash = vectorstore.get(where={"hash": hash_value})
    print(f"Buscando hash {hash_value} en {collection_name}: Encontrados {len(find_hash['documents'])} documentos")
    
    if len(find_hash["documents"]) == 0:
        chunks = dividir_en_chunks(contenido)
        documentos = [
            Document(
                page_content=chunk,
                metadata={
                    "id_document": id_document,   
                    "source": nombre,
                    "hash": hash_value,           
                    "chunk_id": f"{id_document}_chunk{i}",  
                    "category": categoria
                }
            )
            for i, chunk in enumerate(chunks)
        ]
        
        start_time = time.time()
        print(f"Total chunks: {len(documentos)} para {nombre}")
        
        for i in range(0, len(documentos), 32):
            print(f"Procesando: {i+32}/{len(documentos)} - {time.time() - start_time}")
            try:
                vectorstore.add_documents(documentos[i:i+32])
                print(f"Procesado: {i+32}/{len(documentos)} - {time.time() - start_time}", end="\r")
            except Exception as e:
                print(f"Error al añadir documentos: {e}")
        
        print(f"Completado - {time.time() - start_time} segundos")
    else:
        print(f"Archivo {nombre} ya almacenado en {collection_name} con hash {hash_value}")


def buscar_fragmentos_relevantes(pregunta: str, collection_name: str, n_results: int = 3, category_filter: Optional[str] = None) -> List[str]:
    vectorstore = get_chroma_vectorstore(collection_name)
    search_kwargs = {"k": n_results}
    if category_filter:
        search_kwargs["filter"] = {"category": category_filter}
    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    documentos = retriever.invoke(pregunta)
    return [doc.page_content for doc in documentos]