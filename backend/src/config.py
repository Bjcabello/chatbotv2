from pathlib import Path

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


LIMIT_PAGE_PDF = 3
CHROMA_MARKDOWN_COLLECTION = "markdown_index"  
CHROMA_PDF_COLLECTION = "pdf_index"  