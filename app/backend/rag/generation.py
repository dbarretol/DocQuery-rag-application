import logging
import json
from pydantic import TypeAdapter
from app.backend.config_loader import get_generation_model, get_prompt
from app.backend.rag.utils import get_client
from app.backend.rag.retry_config import retry_on_api_errors
from app.backend.rag.models import RAGContext
from app.backend.api_models import ChatResponse, Source

logger = logging.getLogger("uvicorn")

def generate_answer(query: str, context: RAGContext, model_name: str = None, language: str = "Spanish") -> ChatResponse:
    logger.info(f"Generating answer for: '{query}' (model: {model_name or get_generation_model()}, lang: {language})")
    client = get_client()
    
    formatted_context = ""
    sources = []
    
    for i, chunk in enumerate(context.chunks, 1):
        # Format context: content + citation
        formatted_context += f"Source [{i}]:\nContent: {chunk.content}\nSource: {chunk.filename}, Page: {chunk.page}\n\n"
        sources.append(Source(
            id=chunk.id,
            filename=chunk.filename,
            page=chunk.page
        ))
        
    prompt = get_prompt("answer_generation").format(context=formatted_context, query=query, language=language)
    
    model = model_name or get_generation_model()
    
    @retry_on_api_errors
    def _call_gemini():
        return client.models.generate_content(
            model=model,
            contents=prompt
        )
        
    response = _call_gemini()
    logger.info("Answer generated successfully.")
    
    # Ensure unique sources by id
    unique_sources = []
    seen_ids = set()
    for s in sources:
        if s.id not in seen_ids:
            unique_sources.append(s)
            seen_ids.add(s.id)

    return ChatResponse(answer=response.text, sources=unique_sources)

def generate_suggestions(question: str, answer: str, context: RAGContext, language: str = "Spanish"):
    logger.info("Generating follow-up suggestions.")
    client = get_client()
    
    formatted_context = ""
    for chunk in context.chunks:
        formatted_context += f"{chunk.content}\n"
        
    prompt = get_prompt("suggestion_generation").format(
        context=formatted_context, 
        question=question, 
        answer=answer, 
        language=language
    )
    
    @retry_on_api_errors
    def _call_gemini():
        return client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        
    response = _call_gemini()
    logger.info("Suggestions generated successfully.")
    
    # Use TypeAdapter for robust validation
    try:
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        adapter = TypeAdapter(list[str])
        suggestions = adapter.validate_python(data)
        return suggestions
    except Exception as e:
        logger.error(f"Error validating/parsing suggestions JSON: {e}")
        return []
