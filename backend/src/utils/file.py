from pathlib import Path
from  langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader


def cargar_markdown(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"El archivo {path} no existe.")

    loader = UnstructuredMarkdownLoader(str(path))
    data = loader.load()

    if not data or not data[0].page_content.strip():
        raise ValueError(f"El archivo {path} está vacío o no se pudo cargar correctamente.")

    return data[0].page_content
def leer_pdf(path: Path) -> str:
    try:
        loader = PyMuPDFLoader(str(path))
        documents = loader.load()
        texto = "\n".join(doc.page_content for doc in documents)
        return texto.strip()
    except Exception as e:
        raise Exception(f"Error al leer el PDF: {str(e)}")
    

    
# def leer_markdown(path: Path) -> str:
#     with open(path, "r", encoding="utf-8") as f:
#         return f.read().strip()

# def leer_pdf(path: Path) -> str:
#     texto = ""
#     with PyMuPDFLoader.open(path) as pdf:
#         for page in pdf.pages:
#             texto += page.extract_text() + "\n"
#     return texto.strip()

