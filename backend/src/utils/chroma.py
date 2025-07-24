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

def indexar_documento(nombre: str, contenido: str):
    """
    Agrega el contenido del documento a la colección de Chroma.

    Parámetros:
    - nombre: ID único del documento (por ejemplo, nombre del archivo).
    - contenido: Texto plano del documento.
    """
    collection.add(documents=[contenido], ids=[nombre])

def buscar_fragmentos_relevantes(pregunta: str) -> str:
    """
    Busca los fragmentos más relevantes en la colección para una pregunta dada.

    Retorna:
    - Un string concatenado con los fragmentos más relevantes encontrados.
    """
    resultados = collection.query(query_texts=[pregunta], n_results=2)
    return "\n".join(resultados["documents"][0])

def store_pdf_text(text: str, doc_name: str):
    chroma = client
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    docs = [Document(page_content=chunk, metadata={"source": doc_name}) for chunk in chunks]
    chroma.add_documents(docs)
    # chroma.persist()