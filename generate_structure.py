import os
from pathlib import Path

def generate_tree(directory, prefix="", output_file=None, ignore_list=None):
    """
    Genera una representación en texto de la estructura de directorios y archivos.
    :param directory: Directorio raíz a recorrer.
    :param prefix: Prefijo para la representación visual (para indentación).
    :param output_file: Archivo donde se escribirá la estructura.
    :param ignore_list: Lista de nombres de archivos/carpetas a ignorar.
    """
    if ignore_list is None:
        ignore_list = ['.git', 'node_modules', '__pycache__', '.vscode', '.venv']

    # Obtener el nombre de la carpeta raíz
    root_name = os.path.basename(directory)
    print(root_name)
    print(root_name, file=output_file)

    # Obtener todos los elementos del directorio
    items = sorted(Path(directory).iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))

    for index, item in enumerate(items):
        # Ignorar elementos en la lista de exclusión
        if item.name in ignore_list:
            continue

        # Determinar el conector (línea de árbol)
        is_last = index == len(items) - 1
        connector = "└── " if is_last else "├── "
        line = f"{prefix}{connector}{item.name}"
        print(line)
        print(line, file=output_file)

        # Si es un directorio, recorrer recursivamente
        if item.is_dir():
            new_prefix = prefix + ("    " if is_last else "│   ")
            generate_tree(item, new_prefix, output_file, ignore_list)

def main():
    # Directorio actual (raíz del proyecto)
    project_dir = os.getcwd()
    
    # Nombre del archivo de salida
    output_file_path = "project-structure.txt"
    
    # Si el archivo ya existe, eliminarlo
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
    
    # Abrir archivo para escribir la estructura
    with open(output_file_path, 'w', encoding='utf-8') as f:
        generate_tree(project_dir, output_file=f)

if __name__ == "__main__":
    main()