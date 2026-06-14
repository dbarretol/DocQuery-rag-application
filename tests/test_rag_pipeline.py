import pytest
from unittest.mock import MagicMock, patch
from app.backend.rag.ingest import ingest_document
from app.backend.rag.retrieval import retrieve_context
from app.backend.rag.generation import generate_answer
from app.backend.rag.models import RAGContext, DocumentChunk
from app.backend.api_models import ChatResponse

@pytest.mark.asyncio
@patch("app.backend.rag.ingest.get_client")
@patch("app.backend.rag.ingest.get_chroma_client")
@patch("fitz.open")
async def test_ingest_document(mock_fitz, mock_chroma, mock_get_client):
    # Setup mocks
    mock_doc = MagicMock()
    mock_fitz.return_value = mock_doc
    mock_doc.__len__.return_value = 1
    mock_page = MagicMock()
    mock_page.get_text.return_value = "dummy text"
    mock_page.get_images.return_value = []
    mock_doc.__getitem__.return_value = mock_page
    
    mock_collection = MagicMock()
    mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
    
    # Mocking client.models.embed_content
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.models.embed_content.return_value.embeddings = [MagicMock(values=[0.1] * 768)]
    
    # Run ingestion
    result = await ingest_document("dummy.pdf", "dummy.pdf")
    assert result == "INDEXED"
    assert mock_collection.add.called

@patch("app.backend.rag.retrieval.get_client")
@patch("app.backend.rag.retrieval.get_chroma_client")
def test_retrieve_context(mock_chroma, mock_get_client):
    # Setup mocks
    mock_collection = MagicMock()
    mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.models.embed_content.return_value.embeddings = [MagicMock(values=[0.1] * 768)]
    
    mock_collection.query.return_value = {
        "documents": [["text"]], 
        "metadatas": [[{"filename": "test.pdf", "page": 1, "content_type": "text"}]],
        "ids": [["id1"]],
        "distances": [[0.0]]
    }
    
    # Run retrieval
    result = retrieve_context("query")
    assert isinstance(result, RAGContext)
    assert result.chunks[0].content == "text"

@patch("app.backend.rag.generation.get_client")
def test_generate_answer(mock_get_client):
    # Setup mocks
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_response = MagicMock()
    mock_response.text = "The answer is 42."
    # Corregir la metadata para que sean enteros, no MagicMocks
    mock_response.usage_metadata.prompt_token_count = 100
    mock_response.usage_metadata.candidates_token_count = 50
    mock_client.models.generate_content.return_value = mock_response
    # Run generation
    context = RAGContext(chunks=[
        DocumentChunk(id="id1", content="text", filename="test.pdf", page=1, content_type="text")
    ])
    result = generate_answer("question?", context)
    
    assert isinstance(result, ChatResponse)
    assert result.answer == "The answer is 42."
    assert result.sources[0].filename == "test.pdf"
