import os
import chromadb
from chromadb.config import Settings
import logging

logger = logging.getLogger("uvicorn")

def get_chroma_client():
    """
    Returns a persistent ChromaDB client pointing to the path defined in CHROMA_PATH.
    Defaults to './data/chroma' if the environment variable is not set.
    """
    path = os.getenv("CHROMA_PATH", "./data/chroma")
    
    # Ensure the directory exists
    try:
        os.makedirs(path, exist_ok=True)
        logger.info(f"Initializing ChromaDB client at: {path}")
        return chromadb.PersistentClient(path=path)
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB client at {path}: {e}")
        raise
