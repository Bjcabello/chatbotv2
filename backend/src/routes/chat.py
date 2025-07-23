from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.models.chat import Chat
from src.utils.file import leer_markdown
from src.services.chatbot import construir_prompt, enviar_a_ollama
from src.config import BASE_CONTEXT, PROCESSES_CONTEXT
from src.utils.processes import detectar_proceso
from src.utils.chroma import buscar_fragmentos_relevantes

router = APIRouter()

@router.post("/chat")
def chat(data: Chat):
    personalidad = leer_markdown(BASE_CONTEXT / "personality.md")
    logica = leer_markdown(BASE_CONTEXT / "business_logic.md")
    restriccion = leer_markdown(BASE_CONTEXT / "restrictions.md")
    

    nombre_proceso, contenido_proceso = detectar_proceso(data.pregunta, PROCESSES_CONTEXT)
    fragmentos = buscar_fragmentos_relevantes(data.pregunta)

    prompt = construir_prompt(
        data.usuario,
        data.dni,
        data.tipo_usuario,
        data.pregunta,
        personalidad,
        logica,
        contenido_proceso + "\n\n" + fragmentos,
        restriccion
    )

    return StreamingResponse(
        enviar_a_ollama(prompt),
        media_type="text/plain"
    )
