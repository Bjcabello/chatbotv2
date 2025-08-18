# Cargamos un modelo de embeddings ligero para clasificación
from sentence_transformers import SentenceTransformer, util
from src.config import CHROMA_COLLECTION_PDF, CHROMA_COLLECTION_MD


classifier_model = SentenceTransformer("all-MiniLM-L6-v2")


pdf_examples = [
    "¿Qué dice el documento?",
    "Explícame el archivo que subí",
    "Según el PDF que envié",
    "Resume la página 2 del documento",
    "Analiza el texto del archivo",
    "pdf",
    "libro"
    "libros"
    "explicame",
    "archivo",
    "pdf",
    "quiere decir",
    "documento",
    "papel",
    "dime",
    "entender",
    "que",
    "como",
    "cuantos",
    "cuanto",
    "donde",
    "quien"
    "quienes"
]

md_examples = [
    "¿Cuál es la lógica de negocio?",
    "¿Qué restricciones hay?",
    "Describe la personalidad del sistema",
    "Explica las reglas del sistema",
    "Contexto base",
    "eliminar",
    "como creo un usuario?",
    "como edito un usuario?",
    "como borro un usuario?",
    "como actualizo un usuario?",
    "como elimino un usuario?"
    "como se dice perro en ingles",
    "crear",
    "editar",
    "viamatica",
    "instrucciones"
    "gracias"
    "adios"
    "como te llamas?"
]

def detectar_tipo_pregunta(pregunta: str) -> str:
    embedding_pregunta = classifier_model.encode(pregunta, convert_to_tensor=True)

    # Similaridad con ejemplos PDF
    embedding_pdf = classifier_model.encode(pdf_examples, convert_to_tensor=True)
    score_pdf = util.cos_sim(embedding_pregunta, embedding_pdf).max().item()

    # Similaridad con ejemplos Markdown
    embedding_md = classifier_model.encode(md_examples, convert_to_tensor=True)
    score_md = util.cos_sim(embedding_pregunta, embedding_md).max().item()

    print(f"📊 Similitud PDF: {score_pdf:.4f} | Markdown: {score_md:.4f}")

    return CHROMA_COLLECTION_PDF if score_pdf > score_md else CHROMA_COLLECTION_MD