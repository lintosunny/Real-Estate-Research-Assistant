import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from dotenv import load_dotenv


load_dotenv()

class Settings(BaseSettings):

    # API Keys
    groq_api_key: str = os.getenv("GROQ_API_KEY")
    groq_model: str = "llama-3.3-70b-versatile"

    # LLM Configuration
    llm_temparature: float = 0.9
    llm_max_tokens: int = 500 

    # Embedding Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Text Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Vector Store Configuration
    vectorstore_dir: Path = Path(__file__).parent / "data" / "vectorstore"
    collection_name: str = "real_estate_docs"

    # Application Configuration
    app_name: str = "Real Estate Research Tool"
    app_version: str = "1.0.0"
    debug: bool = False

    # Rate Limiting
    max_urls_per_request: int = 10
    max_query_length: int = 500

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/app.log"


    @validator('vectorstore_dir')
    def create_vectorstore_dir(cls, v):
        """Ensure vectorstore directory exists"""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator('groq_api_key')
    def validate_groq_api_key(cls, v):
        """Validate GROQ API key is provided"""
        if not v:
            raise ValueError("GROQ_API_KEY is required")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()