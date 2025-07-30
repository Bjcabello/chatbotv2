from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader

def leer_markdown(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def leer_pdf(path: Path) -> str:
    try:
        loader = PyMuPDFLoader(str(path))
        documents = loader.load()
        texto = "\n".join(doc.page_content for doc in documents)
        return texto.strip()
    except Exception as e:
        raise Exception(f"Error al leer el PDF: {str(e)}")

def detectar_proceso(pregunta: str, procesos_dir: Path) -> tuple[str, str]:
    pregunta = pregunta.lower()
    procesos = {
        "create_user": "crear usuario",
        "update_user": "actualizar usuario",
        "remove_user": "eliminar usuario",
    }

    for nombre, palabra_clave in procesos.items():
        if palabra_clave in pregunta:
            ruta = procesos_dir / f"{nombre}.md"
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read()
                return nombre, contenido
            except FileNotFoundError:
                return nombre, f"No se encontró el archivo para el proceso '{nombre}'"

    return "no_identificado", "No se detectó un proceso relacionado"

