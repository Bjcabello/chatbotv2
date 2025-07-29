# src/chroma.py

from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain.vectorstores.base import VectorStoreRetriever

from src.config import CHROMA_DB_PATH, CHROMA_COLLECTION_NAME, EMBEDDING_MODEL_NAME
from src.file_loader import cargar_pdf_como_chunks

import os

# Configurar embeddings con el modelo BAAI/bge-m3
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

# Inicializar almacén de vectores persistente
def get_chroma_vectorstore():
    return Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )

# Indexar un PDF
def indexar_pdf(nombre_archivo, ruta_pdf):
    chunks = cargar_pdf_como_chunks(ruta_pdf)
    
    # Agregamos metadatos: nombre del archivo
    for chunk in chunks:
        chunk.metadata["origen"] = nombre_archivo

    vectorstore = get_chroma_vectorstore()
    vectorstore.add_documents(chunks)
    vectorstore.persist()

# Buscar fragmentos más relevantes (solo del vector store)
def buscar_en_pdfs(pregunta: str, k=3) -> list[str]:
    vectorstore = get_chroma_vectorstore()
    retriever: VectorStoreRetriever = vectorstore.as_retriever(search_kwargs={"k": k})
    documentos = retriever.get_relevant_documents(pregunta)
    return [doc.page_content for doc in documentos]
