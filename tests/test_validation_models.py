import pytest
from pydantic import ValidationError
from app.backend.api_models import (
    ChatRequest, ChatResponse, Source, SuggestionRequest, 
    GCSConfigRequest
)
from app.backend.rag.models import ChunkMetadata, IngestionStatus, DocumentChunk, RAGContext
from app.backend.storage.models import StorageConfig, GCSConfig

# --- API Models ---
def test_chat_request_validation():
    # Valid
    req = ChatRequest(question="What is RAG?")
    assert req.question == "What is RAG?"
    
    # Invalid (missing question)
    with pytest.raises(ValidationError):
        ChatRequest()

def test_chat_response_validation():
    # Valid
    res = ChatResponse(
        answer="RAG stands for...",
        sources=[Source(id="1", filename="doc.pdf", page=1)]
    )
    assert len(res.sources) == 1
    
    # Invalid (missing answer)
    with pytest.raises(ValidationError):
        ChatResponse()

def test_suggestion_request_validation():
    req = SuggestionRequest(question="Q", answer="A")
    assert req.question == "Q"
    with pytest.raises(ValidationError):
        SuggestionRequest() # Missing required fields

def test_gcs_config_request_validation():
    req = GCSConfigRequest(bucket_name="my-bucket")
    assert req.bucket_name == "my-bucket"
    with pytest.raises(ValidationError):
        GCSConfigRequest()

# --- RAG Models ---
def test_chunk_metadata_validation():
    # Valid
    meta = ChunkMetadata(
        filename="test.txt",
        page=1,
        content_type="text",
        status=IngestionStatus.INDEXED
    )
    assert meta.status == IngestionStatus.INDEXED
    
    # Invalid (invalid status)
    with pytest.raises(ValidationError):
        ChunkMetadata(
            filename="test.txt",
            page=1,
            content_type="text",
            status="INVALID_STATUS"
        )

def test_rag_context_validation():
    chunk = DocumentChunk(id="1", content="text", filename="f", page=1, content_type="text")
    context = RAGContext(chunks=[chunk])
    assert len(context.chunks) == 1

# --- Storage Models ---
def test_storage_config_defaults():
    config = StorageConfig()
    assert config.collection_name == "documents"
    
def test_gcs_config_defaults():
    config = GCSConfig(bucket_name="test")
    assert config.blob_name == "chroma_index.zip"
