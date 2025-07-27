import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURATION CONSTANTS - MODIFY THESE VALUES AS NEEDED
# ============================================================================

# LLM Configuration
GROQ_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.9
LLM_MAX_TOKENS = 500 

# Embedding Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Text Processing
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Vector Store Configuration
VECTORSTORE_DIR = Path(__file__).parent / "data" / "vectorstore"
COLLECTION_NAME = "docs"

# Application Configuration
APP_NAME = "RAG Researcher"
APP_VERSION = "1.0.0"
DEBUG = False

# Rate Limiting
MAX_URLS_PER_REQUEST = 10
MAX_QUERY_LENGTH = 500

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/app.log"

# ============================================================================
# SETTINGS CLASS - DO NOT MODIFY BELOW THIS LINE
# ============================================================================

class Settings(BaseSettings):
    # API Keys - this will come from .env
    groq_api_key: str
    
    # LLM Configuration
    groq_model: str = GROQ_MODEL
    llm_temperature: float = LLM_TEMPERATURE
    llm_max_tokens: int = LLM_MAX_TOKENS

    # Embedding Configuration
    embedding_model: str = EMBEDDING_MODEL

    # Text Processing
    chunk_size: int = CHUNK_SIZE
    chunk_overlap: int = CHUNK_OVERLAP

    # Vector Store Configuration
    vectorstore_dir: Path = VECTORSTORE_DIR
    collection_name: str = COLLECTION_NAME

    # Application Configuration
    app_name: str = APP_NAME
    app_version: str = APP_VERSION
    debug: bool = DEBUG

    # Rate Limiting
    max_urls_per_request: int = MAX_URLS_PER_REQUEST
    max_query_length: int = MAX_QUERY_LENGTH

    # Logging
    log_level: str = LOG_LEVEL
    log_file: Optional[str] = LOG_FILE

    @field_validator('vectorstore_dir')
    @classmethod
    def create_vectorstore_dir(cls, v):
        """Ensure vectorstore directory exists"""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @field_validator('groq_api_key')
    @classmethod
    def validate_groq_api_key(cls, v):
        """Validate GROQ API key is provided"""
        if not v:
            raise ValueError("GROQ_API_KEY is required")
        return v
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        # Only read groq_api_key from environment, others use defaults
        "env_include": {"groq_api_key"}
    }

# Global settings instance
settings = Settings()