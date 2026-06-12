from app.backend.config_loader import get_generation_model, get_prompt
from app.backend.rag.utils import get_client
from app.backend.rag.retry_config import retry_on_api_errors

def generate_answer(query: str, context: dict, model_name: str = None, language: str = "Spanish"):
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
    
    return {"answer": response.text, "sources": list(set(sources))}
