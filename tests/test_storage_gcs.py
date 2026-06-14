import os
from unittest.mock import MagicMock, patch
from app.backend.storage.gcs import download_index, upload_index

@patch("app.backend.storage.gcs.storage.Client")
@patch("app.backend.storage.gcs.unzip_directory")
@patch("app.backend.storage.gcs.os.remove")
@patch("app.backend.storage.gcs.settings")
def test_download_index(mock_settings, mock_remove, mock_unzip, mock_client):
    # Setup mocks
    mock_settings.GCS_BUCKET = "test-bucket"
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.exists.return_value = True
    
    # Run download
    download_index("data/chroma")
    
    assert mock_blob.download_to_filename.called
    assert mock_unzip.called

@patch("app.backend.storage.gcs.storage.Client")
@patch("app.backend.storage.gcs.zip_directory")
@patch("app.backend.storage.gcs.os.remove")
@patch("app.backend.storage.gcs.settings")
def test_upload_index(mock_settings, mock_remove, mock_zip, mock_client):
    # Setup mocks
    mock_settings.GCS_BUCKET = "test-bucket"
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    
    # Run upload
    upload_index("data/chroma")
    
    assert mock_zip.called
    assert mock_blob.upload_from_filename.called
    assert mock_remove.called
