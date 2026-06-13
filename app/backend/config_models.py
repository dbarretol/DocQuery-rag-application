from typing import List
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Config YAML Models ---

class ModelOption(BaseModel):
    name: str
    cost: str = Field(default="N/A")
    description: str

class GenerationConfig(BaseModel):
    default: str
    options: List[ModelOption]

class EmbeddingConfig(BaseModel):
    default: str
    options: List[ModelOption]

class ModelsConfig(BaseModel):
    generation: GenerationConfig
    embeddings: EmbeddingConfig

class PromptsConfig(BaseModel):
    image_description: str
    answer_generation: str
    suggestion_generation: str

class AppConfig(BaseModel):
    models: ModelsConfig
    prompts: PromptsConfig

# --- Environment Settings ---

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    CHROMA_PATH: str = "./data/chroma"
    GEMINI_API_KEY: str
    GCS_BUCKET: str | None = None
