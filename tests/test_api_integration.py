import pytest
from fastapi.testclient import TestClient
from app.backend.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_chat_endpoint_integration():
    # Mocking retrieval and generation to test contract
    with patch("app.backend.main.retrieve_context") as mock_retrieval, \
         patch("app.backend.main.generate_answer") as mock_generation:
        
        mock_retrieval.return_value = MagicMock() # RAGContext
        mock_generation.return_value = {"answer": "RAG is...", "sources": []}
        
        payload = {"question": "What is RAG?"}
        response = client.post("/chat", json=payload)
        
        assert response.status_code == 200
        assert "answer" in response.json()
        assert "sources" in response.json()

def test_chat_suggestions_endpoint_integration():
    with patch("app.backend.main.retrieve_context") as mock_retrieval, \
         patch("app.backend.main.generate_suggestions") as mock_generation:
        
        mock_retrieval.return_value = MagicMock() # RAGContext
        mock_generation.return_value = ["Suggestion 1"]
        
        payload = {"question": "What is RAG?", "answer": "RAG is..."}
        response = client.post("/chat/suggestions", json=payload)
        
        assert response.status_code == 200
        assert response.json() == {"suggestions": ["Suggestion 1"]}

def test_invalid_chat_request():
    # Testing Pydantic validation: send empty payload
    response = client.post("/chat", json={})
    assert response.status_code == 422 # FastAPI Unprocessable Entity
