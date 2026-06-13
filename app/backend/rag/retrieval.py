import logging
from app.backend.storage.chroma import get_chroma_client
from app.backend.config_loader import get_embedding_model
from app.backend.rag.utils import get_client
from app.backend.rag.retry_config import retry_on_api_errors
from app.backend.rag.models import RAGContext, DocumentChunk
from app.backend.storage.models import storage_config

logger = logging.getLogger("uvicorn")

def retrieve_context(query: str, k: int = 5) -> RAGContext:
    logger.info(f"Retrieving context for query: '{query}'")
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
    logger.debug("Query embedded successfully.")
    
    # 2. Query Chroma
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(name=storage_config.collection_name)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=k
    )
    
    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    
    chunks = []
    for doc, meta, doc_id in zip(docs, metadatas, ids):
        chunks.append(DocumentChunk(
            id=doc_id,
            content=doc,
            filename=meta.get("filename", "Unknown"),
            page=meta.get("page", "Unknown"),
            content_type=meta.get("content_type", "text")
        ))
    
    logger.info(f"Retrieved {len(chunks)} documents from ChromaDB.")
    return RAGContext(chunks=chunks)
