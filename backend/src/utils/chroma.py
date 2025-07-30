import uuid
from typing import List
from chromadb.utils import embedding_functions
import chromadb
from src.config import CHROMA_COLLECTION

# Cargar modelo BAAI/bge-m3 como función de embeddings
bge_m3 = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-m3"
)

# Usa almacenamiento persistente en la carpeta 'chroma_db'
client = chromadb.PersistentClient(path="./chroma_db")

# Crear o recuperar la colección usando BGE-M3
collection = client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=bge_m3
)

def dividir_en_chunks(texto: str, max_tokens: int = 300) -> list[str]:
    import textwrap
    # Divide el texto por párrafos primero
    parrafos = texto.split("\n")
    chunks = []
    actual = ""

    for parrafo in parrafos:
        if len(actual) + len(parrafo) < max_tokens:
            actual += parrafo + "\n"
        else:
            chunks.append(actual.strip())
            actual = parrafo + "\n"

    if actual.strip():
        chunks.append(actual.strip())

    return chunks


def indexar_documento(nombre: str, contenido: str):
    """
    Divide e indexa el contenido del documento como chunks con UUIDs y metadatos.
    
    Parámetros:
    - nombre: ID base del documento (usado como metadato).
    - contenido: Texto plano del documento.
    """
    chunks = dividir_en_chunks(contenido)  # Asegúrate de tener esta función correctamente implementada
    ids = [f"{nombre}-{uuid.uuid4()}" for _ in chunks]
    metadatas = [{"documento": nombre} for _ in chunks]  # Aseguramos que todos tengan metadatos

    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas  # <- CLAVE: Siempre debe enviarse esto
    )

    print(f" Documento '{nombre}' indexado con {len(chunks)} fragmentos.")

def buscar_fragmentos_relevantes(pregunta: str) -> str:
    resultados = collection.query(
        query_texts=[pregunta],
        n_results=3
    )

    documentos = resultados.get("documents", [[]])[0]
    metadatas = resultados.get("metadatas", [[]])[0]

    fragmentos = []
    for doc, meta in zip(documentos, metadatas):
        # Usa {} si meta es None
        origen = (meta or {}).get("documento", "desconocido")
        fragmentos.append(f"[{origen}]\n{doc}")

    return "\n\n".join(fragmentos)