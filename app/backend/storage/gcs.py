import os
import logging
from google.cloud import storage

logger = logging.getLogger("uvicorn")

def sync_to_gcs(local_path: str, blob_name: str):
    """
    Optional non-blocking synchronization to GCS.
    If GCS_BUCKET is not defined or connection fails, it logs and continues.
    """
    bucket_name = os.getenv("GCS_BUCKET")
    if not bucket_name:
        logger.info("GCS_BUCKET not defined, skipping GCS sync.")
        return

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)
        logger.info(f"Successfully synced {local_path} to GCS bucket {bucket_name}")
    except Exception as e:
        logger.error(f"Failed to sync to GCS: {e}")
