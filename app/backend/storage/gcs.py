import os
import logging
import zipfile
from google.cloud import storage

logger = logging.getLogger("uvicorn")

def get_gcs_bucket():
    return os.getenv("GCS_BUCKET")

def zip_directory(directory_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), directory_path))

def unzip_directory(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_to)

def download_index(local_path: str):
    """
    Downloads and extracts the ChromaDB index from GCS if GCS_BUCKET is set.
    """
    bucket_name = get_gcs_bucket()
    if not bucket_name:
        logger.info("GCS_BUCKET not defined, skipping GCS download.")
        return
    
    blob_name = "chroma_index.zip"
    zip_path = os.path.join(os.path.dirname(local_path), "chroma_index.zip")
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        if blob.exists():
            blob.download_to_filename(zip_path)
            unzip_directory(zip_path, local_path)
            os.remove(zip_path)
            logger.info(f"Successfully downloaded and extracted index from GCS {bucket_name}")
        else:
            logger.info("No index found in GCS.")
    except Exception as e:
        logger.error(f"Failed to download index from GCS: {e}")

def upload_index(local_path: str):
    """
    Zips and uploads the ChromaDB index to GCS if GCS_BUCKET is set.
    """
    bucket_name = get_gcs_bucket()
    if not bucket_name:
        return
    
    blob_name = "chroma_index.zip"
    zip_path = os.path.join(os.path.dirname(local_path), "chroma_index.zip")
    
    try:
        zip_directory(local_path, zip_path)
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(zip_path)
        os.remove(zip_path)
        logger.info(f"Successfully uploaded index to GCS bucket {bucket_name}")
    except Exception as e:
        logger.error(f"Failed to upload index to GCS: {e}")
