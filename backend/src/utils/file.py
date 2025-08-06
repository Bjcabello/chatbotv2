from pathlib import Path
import pdfplumber
from  langchain_community.document_loaders import PyMuPDFLoader
from src.config import BASE_CONTEXT, PROCESSES_CONTEXT
from src.utils.chroma import indexar_documento

def leer_markdown(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def leer_pdf(path: Path) -> str:
    try:
        loader = PyMuPDFLoader(str(path))
        documents = loader.load()
        texto = "\n".join(doc.page_content for doc in documents)
        return texto.strip()
    except Exception as e:
        raise Exception(f"Error al leer el PDF: {str(e)}")


def indexar_markdowns():
    directorios = [BASE_CONTEXT, PROCESSES_CONTEXT]

    for directorio in directorios:
        for archivo in directorio.glob("*.md"):
            try:
                contenido = leer_markdown(archivo)
                if contenido.strip():
                    indexar_documento(nombre=str(archivo.name), contenido=contenido)
                    print(f" Indexado: {archivo.name}")
            except Exception as e:
                print(f" Error al indexar {archivo.name}: {e}")