from app.backend.rag.generation import generate_suggestions
from unittest.mock import patch, MagicMock
from app.backend.rag.models import RAGContext

def test_generate_suggestions_validation():
    # Simulate a successful LLM call that returns valid JSON list of strings
    mock_response = MagicMock()
    mock_response.text = '["What is RAG?", "How does it work?"]'
    
    with patch("app.backend.rag.generation.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # Call with dummy RAGContext
        context = RAGContext(chunks=[])
        suggestions = generate_suggestions("What is RAG?", "RAG is...", context)
        
        assert suggestions == ["What is RAG?", "How does it work?"]

def test_generate_suggestions_invalid_json():
    # Simulate a successful LLM call that returns invalid JSON
    mock_response = MagicMock()
    mock_response.text = 'invalid json'
    
    with patch("app.backend.rag.generation.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # Call with dummy RAGContext
        context = RAGContext(chunks=[])
        suggestions = generate_suggestions("What is RAG?", "RAG is...", context)
        
        # Should return [] due to exception handling
        assert suggestions == []
