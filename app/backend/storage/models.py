from pydantic import BaseModel

class GCSConfig(BaseModel):
    bucket_name: str
    blob_name: str = "chroma_index.zip"

class StorageConfig(BaseModel):
    chroma_path: str = "./data/chroma"
    collection_name: str = "documents"

storage_config = StorageConfig()
