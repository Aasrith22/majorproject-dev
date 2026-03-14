"""
EduSynapse Backend Configuration
Manages all environment variables and application settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from functools import lru_cache
from pathlib import Path

# Get the absolute path to the backend directory
BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # ===========================================
    # SERVER CONFIGURATION
    # ===========================================
    app_name: str = "EduSynapse"
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # ===========================================
    # DATABASE CONFIGURATION
    # ===========================================
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "edusynapse"
    
    # ===========================================
    # JWT AUTHENTICATION
    # ===========================================
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # ===========================================
    # LLM API KEYS
    # ===========================================
    # Google Gemini Configuration
    google_api_key: str = Field(default="", description="Google Gemini API Key")
    gemini_model: str = "gemini-2.5-flash-lite"
    
    # Tavily Search API (Dynamic Fallback)
    tavily_api_key: str = Field(default="", description="Tavily API Key for dynamic content retrieval")
    tavily_search_depth: str = "advanced"  # "basic" or "advanced"
    
    # ===========================================
    # CREWAI CONFIGURATION
    # ===========================================
    crewai_verbose: bool = True
    crewai_max_retries: int = 3
    crewai_timeout: int = 120
    
    # ===========================================
    # VECTOR STORE CONFIGURATION
    # ===========================================
    vector_index_path: str = "./data/vector_index.npy"
    vector_dimensions: int = 384
    
    # ===========================================
    # EMBEDDING MODEL
    # ===========================================
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # ===========================================
    # KNOWLEDGE BASE
    # ===========================================
    knowledge_base_path: str = "./data/knowledge_base"
    
    # ===========================================
    # CORS CONFIGURATION
    # ===========================================
    cors_origins: str = "http://localhost:8080,http://localhost:3000,http://127.0.0.1:8080"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # ===========================================
    # RATE LIMITING
    # ===========================================
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()


# ===========================================
# LLM PROVIDER CONFIGURATION
# ===========================================
class LLMConfig:
    """Configuration for Gemini LLM provider"""
    
    @staticmethod
    def get_gemini_config():
        """Get Google Gemini configuration"""
        return {
            "api_key": settings.google_api_key,
            "model": settings.gemini_model,
            "temperature": 0.7,
            "max_output_tokens": 8192,
        }
    
    @staticmethod
    def get_active_provider():
        """Get the currently active LLM provider configuration"""
        if settings.google_api_key:
            return "gemini", LLMConfig.get_gemini_config()
        else:
            raise ValueError(
                "No LLM API key configured. Please set GOOGLE_API_KEY in .env"
            )


# ===========================================
# DIFFICULTY LEVELS
# ===========================================
class DifficultyLevels:
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"
    
    ALL = [BEGINNER, EASY, MEDIUM, HARD, EXPERT]


# ===========================================
# ASSESSMENT TYPES
# ===========================================
class AssessmentTypes:
    MCQ = "mcq"
    FILL_IN_BLANK = "fill_in_blank"
    ESSAY = "essay"
    DIAGRAM = "diagram"
    VOICE = "voice"
    
    ALL = [MCQ, FILL_IN_BLANK, ESSAY, DIAGRAM, VOICE]


# ===========================================
# INPUT MODALITIES
# ===========================================
class InputModalities:
    TEXT = "text"
    VOICE = "voice"
    DIAGRAM = "diagram"
    
    ALL = [TEXT, VOICE, DIAGRAM]
