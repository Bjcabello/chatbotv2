from pathlib import Path
import pdfplumber
from  langchain_community.document_loaders import PyMuPDFLoader

def leer_markdown(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

# def leer_pdf(path: Path) -> str:
#     texto = ""
#     with PyMuPDFLoader.open(path) as pdf:
#         for page in pdf.pages:
#             texto += page.extract_text() + "\n"
#     return texto.strip()

def leer_pdf(path: Path) -> str:
    try:
        loader = PyMuPDFLoader(str(path))
        documents = loader.load()
        texto = "\n".join(doc.page_content for doc in documents)
        return texto.strip()
    except Exception as e:
        raise Exception(f"Error al leer el PDF: {str(e)}")
