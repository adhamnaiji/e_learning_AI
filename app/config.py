from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    groq_api_key: str = ""
    perplexity_api_key: str = ""
    
    # Vector Database - IN MEMORY MODE
    qdrant_url: str = ":memory:"  # Changed from localhost
    qdrant_api_key: str = ""
    collection_name: str = "elearning_courses"
    
    # Models
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "llama-3.1-sonar-small-128k-online"
    llm_provider: str = "perplexity"
    
    # Server
    backend_port: int = 8000
    frontend_url: str = "http://localhost:4200"
    
    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }

@lru_cache()
def get_settings():
    return Settings()
