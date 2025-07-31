# 
from langchain_chroma import Chroma
from chromadb.utils import embedding_functions
from src.config import  EMBEDDING_MODEL_NAME, CHROMA_COLLECTION_NAME,CHROMA_DB_PATH
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.docstore.document import Document
# Cargar modelo BAAI/bge-m3 como función de embeddings


# Configurar embeddings con el modelo BAAI/bge-m3
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)


# Inicializar almacén de vectores persistente
def get_chroma_vectorstore():
    return Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )


# Splitting del contenido en chunks
def dividir_en_chunks(texto: str, chunk_size=2000, chunk_overlap=500):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_text(texto)
    return chunks

# Indexación del documento
def indexar_documento(nombre: str, contenido: str):
    # chunks = dividir_en_chunks(contenido)

    # documentos = chunks
    # ids = [f"{nombre}_chunk{i}" for i in range(len(chunks))]

    # vectorstore = get_chroma_vectorstore()
    # vectorstore.add_documents(chunks)
    # vectorstore.persist()
    chunks = dividir_en_chunks(contenido)
    documentos = [Document(page_content=chunk, metadata={"source": nombre, "chunk_id": f"{nombre}_chunk{i}"}) for i, chunk in enumerate(chunks)] #lista de objetos
    vectorstore = get_chroma_vectorstore()
    vectorstore.add_documents(documentos)

# Búsqueda relevante
def buscar_fragmentos_relevantes(pregunta: str, n_results: int = 3) -> str:
    vectorstore = get_chroma_vectorstore()
    retriever: VectorStoreRetriever = vectorstore.as_retriever(search_kwargs={"k": n_results})
    documentos = retriever.invoke(pregunta)
    return [doc.page_content for doc in documentos]
    # resultados = collection.query(query_texts=[pregunta], n_results=n_resultados)
    # return "\n".join(resultados["documents"][0])