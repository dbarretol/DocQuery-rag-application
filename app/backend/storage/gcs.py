import os
import logging
import zipfile
from google.cloud import storage
from app.backend.config_loader import settings
from app.backend.storage.models import GCSConfig

logger = logging.getLogger("uvicorn")

def get_gcs_config() -> GCSConfig | None:
    if not settings.GCS_BUCKET:
        return None
    return GCSConfig(bucket_name=settings.GCS_BUCKET)

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
    gcs_config = get_gcs_config()
    if not gcs_config:
        logger.info("GCS_BUCKET not defined, skipping GCS download.")
        return
    
    zip_path = os.path.join(os.path.dirname(local_path), gcs_config.blob_name)
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(gcs_config.bucket_name)
        blob = bucket.blob(gcs_config.blob_name)
        if blob.exists():
            blob.download_to_filename(zip_path)
            unzip_directory(zip_path, local_path)
            os.remove(zip_path)
            logger.info(f"Successfully downloaded and extracted index from GCS {gcs_config.bucket_name}")
        else:
            logger.info("No index found in GCS.")
    except Exception as e:
        logger.error(f"Failed to download index from GCS: {e}")

def upload_index(local_path: str):
    """
    Zips and uploads the ChromaDB index to GCS if GCS_BUCKET is set.
    """
    gcs_config = get_gcs_config()
    if not gcs_config:
        return
    
    zip_path = os.path.join(os.path.dirname(local_path), gcs_config.blob_name)
    
    try:
        zip_directory(local_path, zip_path)
        storage_client = storage.Client()
        bucket = storage_client.bucket(gcs_config.bucket_name)
        blob = bucket.blob(gcs_config.blob_name)
        blob.upload_from_filename(zip_path)
        os.remove(zip_path)
        logger.info(f"Successfully uploaded index to GCS bucket {gcs_config.bucket_name}")
    except Exception as e:
        logger.error(f"Failed to upload index to GCS: {e}")
