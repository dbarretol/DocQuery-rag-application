import os
import chromadb
import logging

logger = logging.getLogger("uvicorn")

_chroma_client = None

def get_chroma_client():
    """
    Returns a persistent ChromaDB client pointing to the path defined in CHROMA_PATH.
    Uses a global variable to cache the client instance.
    """
    global _chroma_client
    if _chroma_client is None:
        path = os.getenv("CHROMA_PATH", "./data/chroma")
        
        # Ensure the directory exists
        os.makedirs(path, exist_ok=True)
        logger.info(f"Initializing ChromaDB client at: {path}")
        _chroma_client = chromadb.PersistentClient(path=path)
        
    return _chroma_client
