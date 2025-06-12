from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "Puppet Engine"
    
    # Database
    DATABASE_URL: str = "sqlite:///./puppet.db"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Twitter
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_SECRET: Optional[str] = None
    
    # Solana
    SOLANA_RPC_URL: str = "https://api.mainnet-beta.solana.com"
    SOLANA_WALLET_KEY: Optional[str] = None
    
    # Memory Queue
    MEMORY_QUEUE_SIZE: int = 1000
    MEMORY_FLUSH_INTERVAL: int = 60  # seconds
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 