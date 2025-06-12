from typing import List, Dict, Optional
from pydantic import BaseSettings, Field
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI API
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # Twitter API
    twitter_credentials: List[Dict[str, str]] = Field(
        default_factory=list,
        env="TWITTER_CREDENTIALS"
    )
    twitter_bearer_token: Optional[str] = Field(None, env="TWITTER_BEARER_TOKEN")
    
    # Solana
    solana_rpc_url: str = Field(
        "https://api.devnet.solana.com",
        env="SOLANA_RPC_URL"
    )
    jupiter_api_key: Optional[str] = Field(None, env="JUPITER_API_KEY")
    
    # Database
    database_url: str = "sqlite:///marionette.db"
    
    # Testing
    test_mode: bool = False
    test_openai_api_key: Optional[str] = None
    test_twitter_credentials: Optional[List[Dict[str, str]]] = None
    test_solana_rpc_url: str = "https://api.testnet.solana.com"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @classmethod
    def create_env_template(cls) -> None:
        """Create a template .env file if it doesn't exist."""
        env_path = Path(".env")
        if not env_path.exists():
            template = """# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Twitter API
# Format: [{"consumer_key": "key1", "consumer_secret": "secret1", "access_token": "token1", "access_token_secret": "secret1"}, ...]
TWITTER_CREDENTIALS=[{"consumer_key": "your_consumer_key", "consumer_secret": "your_consumer_secret", "access_token": "your_access_token", "access_token_secret": "your_access_token_secret"}]
TWITTER_BEARER_TOKEN=your_bearer_token_here

# Solana
SOLANA_RPC_URL=https://api.devnet.solana.com
JUPITER_API_KEY=your_jupiter_api_key_here

# Testing
TEST_MODE=false
TEST_OPENAI_API_KEY=your_test_openai_api_key_here
TEST_SOLANA_RPC_URL=https://api.testnet.solana.com
"""
            env_path.write_text(template)
            print("Created .env template file. Please fill in your credentials.")

def get_settings() -> Settings:
    """Get application settings."""
    env_file = Path(".env")
    if not env_file.exists():
        # Create template .env file
        template = """# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Twitter (first set)
TWITTER_CONSUMER_KEY_1=your_consumer_key_here
TWITTER_CONSUMER_SECRET_1=your_consumer_secret_here
TWITTER_ACCESS_TOKEN_1=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET_1=your_access_token_secret_here

# Twitter (second set, optional)
TWITTER_CONSUMER_KEY_2=your_consumer_key_here
TWITTER_CONSUMER_SECRET_2=your_consumer_secret_here
TWITTER_ACCESS_TOKEN_2=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET_2=your_access_token_secret_here

# Solana
SOLANA_RPC_URL=https://api.devnet.solana.com
JUPITER_API_KEY=your_jupiter_api_key_here

# Testing
TEST_MODE=false
TEST_OPENAI_API_KEY=your_test_openai_api_key_here
TEST_SOLANA_RPC_URL=https://api.testnet.solana.com
"""
        env_file.write_text(template)
        print("Created .env template file. Please fill in your credentials.")
    
    return Settings()

# Global settings instance
settings = get_settings()

# Create .env template if it doesn't exist
Settings.create_env_template() 