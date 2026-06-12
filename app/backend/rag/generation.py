import google.generativeai as genai
import os
from app.backend.config_loader import get_generation_model

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Using dynamic configuration
model = genai.GenerativeModel(get_generation_model())

def generate_answer(query: str, context: dict):
    # context structure from retrieval: {'documents': [[...]], 'metadatas': [[...]]}
    docs = context.get("documents", [[]])[0]
    metadatas = context.get("metadatas", [[]])[0]
    
    formatted_context = ""
    sources = []
    
    for doc, meta in zip(docs, metadatas):
        # Format context: content + citation
        formatted_context += f"Content: {doc}\nSource: {meta.get('filename')}, Page: {meta.get('page')}\n\n"
        sources.append(f"{meta.get('filename')} (page {meta.get('page')})")
        
    prompt = f"""Use the provided context to answer the question. 
When citing, use the provided source information.
If the answer is not in the context, say so.

Context:
{formatted_context}

Question: {query}

Answer:"""
    
    response = model.generate_content(prompt)
    return {"answer": response.text, "sources": list(set(sources))}
