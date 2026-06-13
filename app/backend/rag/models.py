from pydantic import BaseModel
from enum import Enum

class IngestionStatus(str, Enum):
    PROCESSING = "PROCESSING"
    INDEXED = "INDEXED"
    ERROR = "ERROR"

class DocumentChunk(BaseModel):
    id: str
    content: str
    filename: str
    page: int | str
    content_type: str = "text"

class ChunkMetadata(BaseModel):
    filename: str
    page: int | str
    chunk_index: int | None = None
    img_index: int | None = None
    content_type: str
    status: IngestionStatus = IngestionStatus.INDEXED

class RAGContext(BaseModel):
    chunks: list[DocumentChunk]
