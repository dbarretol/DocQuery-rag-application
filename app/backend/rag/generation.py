import google.generativeai as genai
import os
from app.backend.config_loader import get_generation_model

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Using dynamic configuration
model = genai.GenerativeModel(get_generation_model())

def generate_answer(query: str, context: dict):
    # context is the output from retrieval
    # chroma query results structure: {'documents': [[...]], 'metadatas': [[...]]}
    docs = context.get("documents", [[]])[0]
    metadatas = context.get("metadatas", [[]])[0]
    
    formatted_context = ""
    sources = []
    for doc, meta in zip(docs, metadatas):
        formatted_context += f"- {doc}\n"
        sources.append(f"{meta.get('filename')} (page {meta.get('page')})")
        
    prompt = f"Use the context provided to answer the question. Cite the sources.\n\nQuestion: {query}\n\nContext:\n{formatted_context}\n\nAnswer:"
    
    response = model.generate_content(prompt)
    return {"answer": response.text, "sources": sources}
