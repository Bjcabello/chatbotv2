import requests
import os
from pathlib import Path
from src.utils.file import leer_pdf
from src.utils.chroma import indexar_documento

def subir_libros_gutenberg():
    libros_con_pdf = [84, 98, 1342, 1661, 2701, 2542, 345, 11, 1080, 174]
    temp_dir = Path("temp_gutenberg")
    temp_dir.mkdir(exist_ok=True)

    for libro_id in libros_con_pdf:
        url = f"https://www.gutenberg.org/files/{libro_id}/{libro_id}-pdf.pdf"
        nombre_archivo = temp_dir / f"{libro_id}.pdf"

        print(f"📥 Descargando: {url}")
        response = requests.get(url)

        if response.status_code != 200:
            print(f"⚠️  No encontrado (código {response.status_code}): {url}")
            continue

        with open(nombre_archivo, "wb") as f:
            f.write(response.content)

        try:
            texto = leer_pdf(str(nombre_archivo))
            if not texto.strip():
                print(f"⚠️  El PDF {libro_id} no contiene texto válido.")
                continue

            indexar_documento(nombre=f"Libro-{libro_id}", contenido=texto)
            print(f" {libro_id} indexado en ChromaDB.")

        except Exception as e:
            print(f" Error procesando el libro {libro_id}: {str(e)}")

        finally:
            os.remove(nombre_archivo)

    print(" Proceso completado.")
