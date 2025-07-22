from pathlib import Path

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
