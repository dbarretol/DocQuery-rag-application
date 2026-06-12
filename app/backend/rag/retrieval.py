import os
from google import genai
from app.backend.storage.chroma import get_chroma_client
from app.backend.config_loader import get_embedding_model

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", "dummy_key"))

def retrieve_context(query: str, k: int = 5):
    # 1. Generate query embedding using valid embedding model
    response = client.models.embed_content(
        model=get_embedding_model(),
        contents=query
    )
    embedding = response.embeddings[0].values
    
    # 2. Query Chroma
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(name="documents")
    results = collection.query(
        query_embeddings=[embedding],
        n_results=k
    )
    return results
