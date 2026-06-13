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

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] | None = None

class SuggestionResponse(BaseModel):
    suggestions: list[str]
