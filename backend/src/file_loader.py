# src/file_loader.py

from langchain.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def cargar_pdf_como_chunks(ruta_pdf):
    loader = UnstructuredPDFLoader(ruta_pdf)
    documentos = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=500
    )
    chunks = splitter.split_documents(documentos)
    return chunks
