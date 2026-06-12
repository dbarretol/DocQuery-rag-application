from google import genai
import os
from app.backend.config_loader import get_generation_model

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", "dummy_key"))

def generate_answer(query: str, context: dict, model_name: str = None):
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
        
    prompt = f"""Use the provided context to answer the question. 
When citing, use the provided source information.
If the answer is not in the context, say so.

Context:
{formatted_context}

Question: {query}

Answer:"""
    
    model = model_name or get_generation_model()
    
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    
    return {"answer": response.text, "sources": list(set(sources))}
