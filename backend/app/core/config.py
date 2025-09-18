from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Math Routing Agent"
    debug: bool = False
    
    # Vector store settings
    vector_store_path: str = "data/vector_store"
    knowledge_base_path: str = "data/math_dataset.json"
    feedback_data_path: str = "data/feedback_data.json"
    
    # Model settings
    max_tokens: int = 1000
    temperature: float = 0.1
    
    # Guardrails settings
    max_input_length: int = 1000
    allowed_topics: list = ["mathematics", "math", "algebra", "calculus", "geometry", "trigonometry", "statistics", "probability"]
    
    # Search settings
    search_results_limit: int = 5
    confidence_threshold: float = 0.7
    
    # Feedback settings
    feedback_threshold: int = 3  # Minimum feedback score for acceptance
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()