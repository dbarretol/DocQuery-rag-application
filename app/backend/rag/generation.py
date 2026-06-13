import logging
from app.backend.config_loader import get_generation_model, get_prompt
from app.backend.rag.utils import get_client
from app.backend.rag.retry_config import retry_on_api_errors

logger = logging.getLogger("uvicorn")

def generate_answer(query: str, context: dict, model_name: str = None, language: str = "Spanish"):
    logger.info(f"Generating answer for: '{query}' (model: {model_name or get_generation_model()}, lang: {language})")
    client = get_client()
    # context structure from retrieval: {'documents': [[...]], 'metadatas': [[...]]}
    docs = context.get("documents", [[]])[0]
    metadatas = context.get("metadatas", [[]])[0]
    
    formatted_context = ""
    sources = []
    
    for doc, meta in zip(docs, metadatas):
        # Format context: content + citation
        filename = meta.get('filename', 'Unknown')
        page = meta.get('page', 'Unknown')
        formatted_context += f"Content: {doc}\nSource: {filename}, Page: {page}\n\n"
        sources.append(f"{filename} (page {page})")
        
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
    
    return {"answer": response.text, "sources": list(set(sources))}

def generate_suggestions(question: str, answer: str, context: dict, language: str = "Spanish"):
    logger.info("Generating follow-up suggestions.")
    client = get_client()
    
    docs = context.get("documents", [[]])[0]
    metadatas = context.get("metadatas", [[]])[0]
    
    formatted_context = ""
    for doc, meta in zip(docs, metadatas):
        formatted_context += f"{doc}\n"
        
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
    
    # Simple JSON extraction as prompt asks for JSON array
    import json
    try:
        # Clean response if it contains markdown code blocks
        text = response.text.replace("```json", "").replace("```", "").strip()
        suggestions = json.loads(text)
        return suggestions
    except Exception as e:
        logger.error(f"Error parsing suggestions JSON: {e}")
        return []
