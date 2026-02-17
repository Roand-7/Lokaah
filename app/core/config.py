from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import List

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    
    # AI APIs
    ANTHROPIC_API_KEY: str = ""  # Compatibility only; not used in runtime paths.
    GEMINI_API_KEY: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # App
    APP_NAME: str = "LOKAAH API"
    ENV: str = "production"
    DEBUG: bool = False
    PORT: int = 8000
    CORS_ORIGINS: str = "*"
    
    # Hybrid Oracle
    AI_RATIO: float = 0.5
    
    class Config:
        # Find .env file in project root
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return origins or ["*"]

    @property
    def has_gemini_auth(self) -> bool:
        return bool(
            self.GEMINI_API_KEY
            or (self.GOOGLE_APPLICATION_CREDENTIALS and self.GOOGLE_CLOUD_PROJECT)
        )

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
