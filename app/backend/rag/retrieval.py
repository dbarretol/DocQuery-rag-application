from app.backend.storage.chroma import get_chroma_client
from app.backend.config_loader import get_embedding_model
from app.backend.rag.utils import get_client
from app.backend.rag.retry_config import retry_on_api_errors

def retrieve_context(query: str, k: int = 5):
    client = get_client()
    
    @retry_on_api_errors
    def _embed():
        return client.models.embed_content(
            model=get_embedding_model(),
            contents=query
        )
        
    # 1. Generate query embedding using valid embedding model
    response = _embed()
    embedding = response.embeddings[0].values
    
    # 2. Query Chroma
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(name="documents")
    results = collection.query(
        query_embeddings=[embedding],
        n_results=k
    )
    return results
