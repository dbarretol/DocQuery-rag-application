from fastapi.testclient import TestClient
from app.backend.main import app
from unittest.mock import patch, MagicMock
import os

client = TestClient(app)

@patch("app.backend.main.ingest_document")
def test_upload_document(mock_ingest):
    # Create a dummy file
    with open("test_file.txt", "w") as f:
        f.write("dummy content")
    
    with open("test_file.txt", "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("test_file.txt", f, "text/plain")},
            data={"generation_model": "gemini-3.1-flash-lite", "embedding_model": "gemini-embedding-2"}
        )
    
    assert response.status_code == 200
    assert response.json()["filename"] == "test_file.txt"
    mock_ingest.assert_called_once()
    
    # Cleanup
    os.remove("test_file.txt")

@patch("app.backend.main.get_chroma_client")
def test_get_knowledge_base(mock_chroma):
    mock_collection = MagicMock()
    mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
    mock_collection.get.return_value = {
        "metadatas": [{"filename": "doc1.txt", "content_type": "text"}]
    }
    
    response = client.get("/knowledge-base")
    assert response.status_code == 200
    assert len(response.json()["documents"]) == 1
    assert response.json()["documents"][0]["filename"] == "doc1.txt"

@patch("app.backend.main.get_chroma_client")
def test_get_passage_not_found(mock_chroma):
    mock_collection = MagicMock()
    mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
    mock_collection.get.return_value = {"documents": []}
    
    response = client.get("/passage/nonexistent")
    assert response.status_code == 404
