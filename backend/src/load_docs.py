from src.utils.file import leer_pdf
from src.utils.chroma import indexar_documento
from src.config import DOCUMENTS_CONTEXT
from pathlib import Path

def cargar_pdfs():
    for archivo in DOCUMENTS_CONTEXT.glob("*.pdf"):
        nombre = archivo.stem
        contenido = leer_pdf(archivo)
        if contenido:
            indexar_documento(nombre, contenido)
            print(f" PDF '{nombre}' Agregado.")
        else:
            print(f" No se pudo extraer texto del PDF '{nombre}'")

if __name__ == "__main__":
    cargar_pdfs()
