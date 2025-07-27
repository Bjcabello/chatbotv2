import chromadb
from chromadb.utils import embedding_functions
from src.config import CHROMA_COLLECTION
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
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

# Splitting del contenido en chunks
def dividir_en_chunks(texto: str, chunk_size=500, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_text(texto)
    return chunks

# Indexación del documento
def indexar_documento(nombre: str, contenido: str):
    chunks = dividir_en_chunks(contenido)

    documentos = chunks
    ids = [f"{nombre}_chunk{i}" for i in range(len(chunks))]

    collection.add(documents=documentos, ids=ids)

# Búsqueda relevante
def buscar_fragmentos_relevantes(pregunta: str, n_resultados: int = 3) -> str:
    resultados = collection.query(query_texts=[pregunta], n_results=n_resultados)
    return "\n".join(resultados["documents"][0])