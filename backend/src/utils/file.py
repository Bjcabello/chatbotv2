from pathlib import Path
import pdfplumber

def leer_markdown(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def leer_pdf(path: Path) -> str:
    texto = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() + "\n"
    return texto.strip()
