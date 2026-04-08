"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
    # Database
    DATABASE_URL: str = "mysql+aiomysql://root:password@localhost:3306/todolist"
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:5173"]'
    
    # Server
    DEBUG: bool = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from JSON string"""
        return json.loads(self.CORS_ORIGINS)


settings = Settings()
