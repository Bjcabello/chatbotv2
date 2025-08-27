from pathlib import Path
import pdfplumber
from  langchain_community.document_loaders import PyMuPDFLoader
from src.config import BASE_CONTEXT, PROCESSES_CONTEXT, CHROMA_COLLECTION_MD, LIMIT_PAGE_PDF
from src.utils.chroma import indexar_documento

def leer_markdown(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def count_pages_pdf(documents: str) -> int:
    return documents[0].metadata.get('total_pages', 0)  # Usamos get para evitar errores si no existe


def leer_pdf(path: Path) -> str:
    try:
        loader = PyMuPDFLoader(str(path))
        documents = loader.load()
        print(f"impriminedo el documents {documents}  \n")

        total_pages = count_pages_pdf(documents)

        if total_pages > LIMIT_PAGE_PDF:
            print(" **** excedio el numero de paginas  *** ")
            raise Exception(f"El archivo tiene {total_pages} páginas, excede el límite de {LIMIT_PAGE_PDF} paginas.")

        print(f"\n ---Número total de páginas: {total_pages} \n")
     
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
                    indexar_documento(nombre=str(archivo.name), contenido=contenido, collection_name=CHROMA_COLLECTION_MD)
                    print(f" Indexado: {archivo.name}")
            except Exception as e:
                print(f" Error al indexar {archivo.name}: {e}")