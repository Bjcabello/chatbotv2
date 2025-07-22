import chromadb
from chromadb.utils import embedding_functions
from src.config import CHROMA_COLLECTION

client = chromadb.Client()
collection = client.get_or_create_collection(CHROMA_COLLECTION)

def indexar_documento(nombre, contenido):
    collection.add(documents=[contenido], ids=[nombre])

def buscar_fragmentos_relevantes(pregunta: str) -> str:
    resultados = collection.query(query_texts=[pregunta], n_results=2)
    return "\n".join(resultados["documents"][0])
