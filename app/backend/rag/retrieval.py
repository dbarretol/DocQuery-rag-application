import google.generativeai as genai
from app.backend.storage.chroma import get_chroma_client
import os
from app.backend.config_loader import get_embedding_model

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def retrieve_context(query: str, k: int = 5):
    # 1. Generate query embedding using valid embedding model
    embedding = genai.embed_content(
        model=get_embedding_model(),
        content=query,
        task_type="retrieval_query"
    )["embedding"]
    
    # 2. Query Chroma
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(name="documents")
    results = collection.query(
        query_embeddings=[embedding],
        n_results=k
    )
    return results
