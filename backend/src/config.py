from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
BASE_CONTEXT = BASE_DIR / "context" / "base"
PROCESSES_CONTEXT = BASE_DIR / "context" / "processes"
DOCUMENTS_CONTEXT = BASE_DIR / "context" / "documents"

OLLAMA_URL = "http://localhost:11434/api/chat"
CHROMA_MARKDOWN_COLLECTION = "markdown_index"  
CHROMA_PDF_COLLECTION = "pdf_index"  

EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
CHROMA_DB_PATH = "./chroma_db"



from decouple import config
import os
load_dotenv()

MONGO_URI = config('MONGO_URI')
MONGO_DB_NAME = config('MONGO_DB_NAME')
MONGO_COLLECTION_NAME = config('MONGO_COLLECTION_NAME')
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.urandom(32).hex())
DEFAULT_USERNAME = config('DEFAULT_USERNAME')
DEFAULT_PASSWORD = config('DEFAULT_PASSWORD')