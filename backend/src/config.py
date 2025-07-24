from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


BASE_CONTEXT = BASE_DIR / "src" / "context" / "base"
PROCESSES_CONTEXT = BASE_DIR / "src" / "context" / "processes"
DOCUMENTS_CONTEXT = BASE_DIR / "src" / "context" / "documents"


OLLAMA_URL = "http://localhost:11434/api/chat"
CHROMA_COLLECTION = "procesos_indexados"
