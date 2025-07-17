from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Puppet Engine"
    debug: bool = False
    log_level: str = "INFO"
    # Database
    sqlite_db_path: str = "puppet_engine.db"
    redis_url: str = "redis://localhost:6379"
    
    # Twitter/X API
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    
    # Solana
    solana_rpc_url: str = "https://api.mainnet-beta.solana.com"
    solana_private_key: Optional[str] = None
    
    # Security
    secret_manager: str = "env"  # env, vault, aws-secrets-manager
    vault_addr: Optional[str] = None
    vault_token: Optional[str] = None
    vault_path: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 