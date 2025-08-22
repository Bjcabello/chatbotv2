from pathlib import Path
from src.config import BASE_CONTEXT, PROCESSES_CONTEXT, CHROMA_MARKDOWN_COLLECTION, CHROMA_PDF_COLLECTION
from src.utils.chroma import indexar_documento
from langchain_community.document_loaders import PyMuPDFLoader

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
    for archivo in BASE_CONTEXT.glob("*.md"):
        try:
            contenido = leer_markdown(archivo)
            if contenido.strip():
                indexar_documento(nombre=str(archivo.name), contenido=contenido, collection_name=CHROMA_MARKDOWN_COLLECTION, categoria="base")
                print(f"Indexado: {archivo.name} (base)")
        except Exception as e:
            print(f"Error al indexar {archivo.name}: {e}")

    for archivo in PROCESSES_CONTEXT.glob("*.md"):
        try:
            contenido = leer_markdown(archivo)
            if contenido.strip():
                indexar_documento(nombre=str(archivo.name), contenido=contenido, collection_name=CHROMA_MARKDOWN_COLLECTION, categoria="processes")
                print(f"Indexado: {archivo.name} (processes)")
        except Exception as e:
            print(f"Error al indexar {archivo.name}: {e}")

def indexar_pdf(nombre: str, contenido: str):
    if contenido.strip():
        indexar_documento(nombre=nombre, contenido=contenido, collection_name=CHROMA_PDF_COLLECTION, categoria="pdf")
        print(f"Indexado: {nombre} (pdf)")