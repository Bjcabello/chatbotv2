from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
BASE_CONTEXT = BASE_DIR / "context" / "base"
PROCESSES_CONTEXT = BASE_DIR / "context" / "processes"
DOCUMENTS_CONTEXT = BASE_DIR / "context" / "documents"

OLLAMA_URL = "http://localhost:11434/api/chat"
CHROMA_COLLECTION = "procesos_indexados"


EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
CHROMA_DB_PATH = "./chroma_db"
# CHROMA_COLLECTION_NAME = "documentos_pdf"

CHROMA_COLLECTION_PDF = "documentos_pdf"
CHROMA_COLLECTION_MD = "documentos_md"


LIMIT_PAGE_PDF = 30
CHROMA_MARKDOWN_COLLECTION = "markdown_index"  
CHROMA_PDF_COLLECTION = "pdf_index"  

# from decouple import config
# import os
# load_dotenv()

# MONGO_URI = os.getenv('MONGO_URI')
# MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
# MONGO_COLLECTION_NAME = os.getenv('MONGO_COLLECTION_NAME')
# JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
# DEFAULT_USERNAME = os.getenv('DEFAULT_USERNAME')
# DEFAULT_PASSWORD = os.getenv('DEFAULT_PASSWORD')