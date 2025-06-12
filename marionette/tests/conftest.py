import pytest
import asyncio
import os
from ..memory.database import db
from unittest.mock import AsyncMock, MagicMock, patch
from ..config.settings import settings
from ..llm.client import LLMClient
from ..twitter.client import TwitterClient
from ..solana.client import SolanaClient

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Set up a test database for the session."""
    # Use a separate test database
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    
    # Initialize the database
    await db.initialize()
    
    yield db
    
    # Clean up
    await db.close()
    if os.path.exists("test.db"):
        os.remove("test.db")

@pytest.fixture(autouse=True)
async def setup_test_db(test_db):
    """Set up and tear down the test database for each test."""
    # The database is already initialized by test_db fixture
    yield
    
    # Clean up any test data
    async with test_db.connect() as conn:
        await conn.execute("DELETE FROM relationships")
        await conn.execute("DELETE FROM memories")
        await conn.execute("DELETE FROM agents")
        await conn.commit()

@pytest.fixture(scope="session")
def llm_client():
    """Create LLM client for testing."""
    if settings.test_mode and settings.test_openai_api_key:
        return LLMClient(api_key=settings.test_openai_api_key.get_secret_value())
    return LLMClient(api_key=settings.openai_api_key.get_secret_value())

@pytest.fixture(scope="session")
def twitter_client():
    """Create Twitter client for testing."""
    if settings.test_mode and settings.test_twitter_credentials:
        creds = settings.test_twitter_credentials
    else:
        creds = settings.twitter_credentials
    return TwitterClient(credentials=creds)

@pytest.fixture(scope="session")
def solana_client():
    """Create Solana client for testing."""
    rpc_url = settings.test_solana_rpc_url if settings.test_mode else settings.solana_rpc_url
    return SolanaClient(rpc_url=rpc_url)

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("TEST_MODE", "true")
    if not settings.test_openai_api_key:
        monkeypatch.setenv("TEST_OPENAI_API_KEY", "test_openai_key")
    if not settings.test_twitter_credentials:
        monkeypatch.setenv("TWITTER_CONSUMER_KEY_1", "test_consumer_key")
        monkeypatch.setenv("TWITTER_CONSUMER_SECRET_1", "test_consumer_secret")
        monkeypatch.setenv("TWITTER_ACCESS_TOKEN_1", "test_access_token")
        monkeypatch.setenv("TWITTER_ACCESS_TOKEN_SECRET_1", "test_access_token_secret")

@pytest.fixture(autouse=True)
def mock_async_sleep(monkeypatch):
    """Mock asyncio.sleep to speed up tests."""
    async def mock_sleep(*args, **kwargs):
        pass
    monkeypatch.setattr("asyncio.sleep", mock_sleep) 