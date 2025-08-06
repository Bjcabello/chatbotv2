# from src.utils.file import leer_pdf
# from src.utils.chroma import indexar_documento
# from src.config import DOCUMENTS_CONTEXT
# from pathlib import Path

# def cargar_pdfs():
#     for archivo in DOCUMENTS_CONTEXT.glob("*.pdf"):
#         nombre = archivo.stem
#         contenido = leer_pdf(archivo)
#         if contenido:
#             indexar_documento(nombre, contenido)
#             print(f" PDF '{nombre}' Agregado.")
#         else:
#             print(f" No se pudo extraer texto del PDF '{nombre}'")

# if __name__ == "__main__":
#     cargar_pdfs()
from src.config import BASE_CONTEXT
from src.utils.file import cargar_markdown

def test_markdowns():
    archivos = ["personality.md", "business_logic.md", "restrictions.md"]

    for archivo in archivos:
        path = BASE_CONTEXT / archivo
        print(f"Probando archivo: {path}")
        try:
            contenido = cargar_markdown(path)
            print(f"✅ {archivo} cargado con éxito. Primeros 200 caracteres:\n")
            print(contenido[:200])
            print("-" * 50)
        except Exception as e:
            print(f"❌ Error al cargar {archivo}: {e}")

if __name__ == "__main__":
    test_markdowns()
