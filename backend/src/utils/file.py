from pathlib import Path
import pdfplumber
from  langchain_community.document_loaders import PyMuPDFLoader
from src.config import BASE_CONTEXT, PROCESSES_CONTEXT, CHROMA_COLLECTION_MD, LIMIT_PAGE_PDF, CHROMA_PDF_COLLECTION, CHROMA_MARKDOWN_COLLECTION
from src.utils.chroma import indexar_documento

def leer_markdown(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def count_pages_pdf(documents: str) -> int:
    return documents[0].metadata.get('total_pages', 0)  # Usamos get para evitar errores si no existe


def leer_pdf(path: Path) -> str:
    try:
        print(f"contenido del path subido: {path}")
        print(f"type del path subido {type(path)}  \n")
        loader = PyMuPDFLoader(str(path))
        documents = loader.load()
        print(f"imprimiendo el documents {documents}  \n")

        total_pages = count_pages_pdf(documents)

        if total_pages > LIMIT_PAGE_PDF:
            print(" **** excedio el numero de paginas  *** ")
            raise Exception(f"El archivo tiene {total_pages} páginas, excede el límite de {LIMIT_PAGE_PDF} paginas.")

        print(f"\n ---Número total de páginas: {total_pages} \n")
     
        texto = "\n".join(doc.page_content for doc in documents)
        print(f"imprimiendo texto: {texto}")
        
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