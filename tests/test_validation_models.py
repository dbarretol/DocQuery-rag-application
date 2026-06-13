import pytest
from pydantic import ValidationError
from app.backend.api_models import ChatRequest, ChatResponse, Source
from app.backend.rag.models import ChunkMetadata, IngestionStatus
from app.backend.storage.models import StorageConfig

def test_chat_request_validation():
    # Valid
    req = ChatRequest(question="What is RAG?")
    assert req.question == "What is RAG?"
    assert req.language == "Spanish"
    
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
        ChatResponse(sources=[])

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

def test_storage_config_defaults():
    config = StorageConfig()
    assert config.collection_name == "documents"
    assert config.chroma_path == "./data/chroma"
