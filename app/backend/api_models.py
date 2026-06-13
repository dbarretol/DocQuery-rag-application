from pydantic import BaseModel

# --- Request Models ---

class ChatRequest(BaseModel):
    question: str
    generation_model: str | None = None
    language: str = "Spanish"

class SuggestionRequest(BaseModel):
    question: str
    answer: str
    language: str = "Spanish"

# --- Response Models ---

class Source(BaseModel):
    id: str
    filename: str
    page: int | str

class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] | None = None

class SuggestionResponse(BaseModel):
    suggestions: list[str]

class UploadResponse(BaseModel):
    message: str
    filename: str

class DocumentStatusResponse(BaseModel):
    status: str

class DocumentInfo(BaseModel):
    filename: str
    content_type: str

class KnowledgeBaseResponse(BaseModel):
    documents: list[DocumentInfo]

class PassageResponse(BaseModel):
    content: str
    metadata: dict
    type: str
