import yaml
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "../../config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

def get_generation_model():
    return config["models"]["generation"]["default"]

def get_embedding_model():
    return config["models"]["embeddings"]["default"]
