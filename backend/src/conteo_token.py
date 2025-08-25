import tiktoken  # Librería para contar tokens (aproximación para Mistral)

# Inicializa el encoding (cl100k_base es una buena aproximación para modelos como Mistral)
encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Cuenta tokens usando tiktoken."""
    if not text:
        return 0
    return len(encoding.encode(text))

