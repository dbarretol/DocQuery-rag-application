import os
import chromadb
import logging
from app.backend.config_loader import settings
from app.backend.storage.models import StorageConfig

logger = logging.getLogger("uvicorn")

_chroma_client = None

def get_chroma_client():
    """
    Returns a persistent ChromaDB client pointing to the path defined in CHROMA_PATH.
    Uses a global variable to cache the client instance.
    """
    global _chroma_client
    if _chroma_client is None:
        storage_config = StorageConfig(chroma_path=settings.CHROMA_PATH)
        path = storage_config.chroma_path

        # Ensure the directory exists
        os.makedirs(path, exist_ok=True)
        logger.info(f"Initializing ChromaDB client at: {path}")
        _chroma_client = chromadb.PersistentClient(path=path)
        
    return _chroma_client
