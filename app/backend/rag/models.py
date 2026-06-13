from pydantic import BaseModel

class DocumentChunk(BaseModel):
    id: str
    content: str
    filename: str
    page: int | str
    content_type: str = "text"

class RAGContext(BaseModel):
    chunks: list[DocumentChunk]
