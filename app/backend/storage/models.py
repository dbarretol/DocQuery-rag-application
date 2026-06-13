from pydantic import BaseModel

class GCSConfig(BaseModel):
    bucket_name: str
    blob_name: str = "chroma_index.zip"

class StorageConfig(BaseModel):
    chroma_path: str = "./data/chroma"
