from app.backend.storage.chroma import get_chroma_client
from app.backend.config_loader import get_embedding_model
from app.backend.rag.utils import get_client

def retrieve_context(query: str, k: int = 5):
    client = get_client()
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
