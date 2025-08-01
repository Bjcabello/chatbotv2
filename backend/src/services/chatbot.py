import requests
import json
from src.config import OLLAMA_URL

def construir_prompt(usuario, dni, tipo_usuario,  personalidad, logica, contenido_proceso, pregunta, restriccion):
    prompt = f"""

    Personalidad:
    {personalidad}

    Lógica del negocio:
    {logica}

    Contexto relacionado:
    {contenido_proceso}

    Usuario: {usuario} (DNI: {dni}, tipo: {tipo_usuario})

    Pregunta:
    {pregunta}

    Restricciones:
    {restriccion}
    
    """
    return prompt.strip()

def enviar_a_ollama(prompt: str):
    payload = {
        "model": "llama2",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        yield chunk
    except Exception as e:
        yield f"\n Error: {e}"
