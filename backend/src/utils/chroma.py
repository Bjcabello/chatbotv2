# 
from langchain_chroma import Chroma
from src.config import  EMBEDDING_MODEL_NAME, CHROMA_DB_PATH
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.docstore.document import Document
from typing import Optional, List, Dict

# Cargar modelo BAAI/bge-m3 como función de embeddings


# Configurar embeddings con el modelo BAAI/bge-m3
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

# Inicializar almacén de vectores persistente
def get_chroma_vectorstore(collection_name: str):
    return Chroma(
        # collection_name=CHROMA_COLLECTION_NAME,
        collection_name=collection_name,
        embedding_function=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )

def dividir_en_chunks(texto: str, chunk_size=600, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_text(texto)
    return chunks

import hashlib

def generar_hash(texto: str) -> str:
    if not isinstance(texto, str):
        raise ValueError("El input debe ser un string")
    
    # Convertir el string a bytes y generar el hash
    hash_obj = hashlib.sha256(texto.encode('utf-8'))
    return hash_obj.hexdigest()

# Indexación del documento
def indexar_documento(nombre: str, contenido: str, collection_name: str, categoria: str):
    vectorstore = get_chroma_vectorstore(collection_name)
        
    hash = generar_hash(contenido) 
    
    find_hash = vectorstore.get(where={"hash": hash})
    
    if len(find_hash["documents"]) == 0:
        chunks = dividir_en_chunks(contenido)
        documentos = [Document(page_content=chunk, metadata={"source": nombre, "hash": hash, "chunk_id": f"{hash}_chunk{i}","category": categoria}) for i, chunk in enumerate(chunks)] #lista de objetos
    
        import time
        start_time = time.time()
        print(f"start_time: {start_time}")
    
        print(f"total chunks: {len(documentos)}")
    
        for i in range(0, len(documentos), 32):
            print(f"processing: {i+32}/{len(documentos)} - {time.time() - start_time}") 
            vectorstore.add_documents(documentos[i:i+32])
            print(f"processed: {i+32}/{len(documentos)} - {time.time() - start_time}", end="\r") 
        
        print(f"completed - {time.time() - start_time}")
    else:
        print("archivo almacenado en chromadb previamente")
    
    
# Búsqueda relevante
# def buscar_fragmentos_relevantes(pregunta: str, collection_name: str, n_results: int = 3, category_filter: Optional[str] = None) -> List[str]:
#     vectorstore = get_chroma_vectorstore(collection_name)
#     # retriever: VectorStoreRetriever = vectorstore.as_retriever(search_kwargs={"k": n_results})
#     # documentos = retriever.invoke(pregunta)
#     # return [doc.page_content for doc in documentos]
#     search_kwargs = {"k": n_results}
#     if category_filter:
#         search_kwargs["filter"] = {"category": category_filter}
#     retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
#     documentos = retriever.invoke(pregunta)
#     return [doc.page_content for doc in documentos]
def buscar_fragmentos_relevantes(pregunta: str, collection_name: str, n_results: int = 3, category_filter: Optional[str] = None) -> List[str]:
    vectorstore = get_chroma_vectorstore(collection_name)
    search_kwargs = {"k": n_results}
    if category_filter:
        search_kwargs["filter"] = {"category": category_filter}
    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    documentos = retriever.invoke(pregunta)
    return [doc.page_content for doc in documentos]



