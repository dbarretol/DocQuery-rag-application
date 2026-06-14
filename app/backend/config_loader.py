import yaml
import os
from .config_models import AppConfig, Settings

def load_app_config() -> AppConfig:
    config_path = os.path.join(os.path.dirname(__file__), "../config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return AppConfig(**data)

# Initialize models
config = load_app_config()
settings = Settings()

def get_generation_model():
    return config.models.generation.default

def get_embedding_model():
    return config.models.embeddings.default

def get_prompt(prompt_key):
    return getattr(config.prompts, prompt_key)
