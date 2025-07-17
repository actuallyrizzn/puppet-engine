import pytest
import asyncio
import logging
import os
from unittest.mock import AsyncMock, MagicMock
from src.core.settings import Settings
from src.memory.base import MemoryStore, VectorStore
from src.llm.base import BaseLLMProvider
from src.events.engine import EventEngine
from src.agents.agent_manager import AgentManager

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
async def cancel_asyncio_tasks_after_test():
    yield
    # Cancel all running asyncio tasks except the current one
    current_task = asyncio.current_task()
    tasks = [t for t in asyncio.all_tasks() if t is not current_task]
    if tasks:
        logger.debug(f"Cancelling {len(tasks)} leftover asyncio tasks after test...")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

# Hard exit at session finish if pytest hangs

# def pytest_sessionfinish(session, exitstatus):
#     logger.info("pytest_sessionfinish: Forcing process exit to avoid hang.")
#     os._exit(exitstatus)

def pytest_configure(config):
    # Warn if someone forgot to set the env-var on CI
    if not os.getenv("PYTHONASYNCIODEBUG"):
        os.environ["PYTHONASYNCIODEBUG"] = "1"

@pytest.fixture
async def settings():
    """Provide test settings."""
    return Settings(
        openai_api_key="test-key",
        grok_api_key="test-key",
        twitter_bearer_token="test-token",
        twitter_api_key="test-key",
        twitter_api_secret="test-secret",
        twitter_access_token="test-token",
        twitter_access_token_secret="test-secret",
        solana_private_key="test-key",
        solana_rpc_url="https://api.mainnet-beta.solana.com",
        mongodb_uri="mongodb://localhost:27017/test",
        vector_store_uri="mongodb://localhost:27017/test",
        log_level="DEBUG"
    )

@pytest.fixture
async def mock_memory_store():
    """Provide a mock memory store."""
    store = AsyncMock(spec=MemoryStore)
    store.store_memory = AsyncMock()
    store.get_memory = AsyncMock(return_value=None)
    store.search_memories = AsyncMock(return_value=[])
    store.get_agent_memories = AsyncMock(return_value=[])
    store.delete_memory = AsyncMock(return_value=True)
    store.update_memory = AsyncMock(return_value=None)
    return store

@pytest.fixture
async def mock_vector_store():
    """Provide a mock vector store."""
    store = AsyncMock(spec=VectorStore)
    store.store_embedding = AsyncMock(return_value=True)
    store.search_similar = AsyncMock(return_value=[])
    store.delete_embedding = AsyncMock(return_value=True)
    return store

@pytest.fixture
async def mock_llm_provider():
    """Provide a mock LLM provider."""
    provider = AsyncMock(spec=BaseLLMProvider)
    provider.config = {"model": "gpt-4", "max_tokens": 1024, "temperature": 0.7}
    provider.model = "gpt-4"
    provider.max_tokens = 1024
    provider.temperature = 0.7
    provider.generate_content = AsyncMock(return_value=AsyncMock(content="Test response", model="gpt-4"))
    provider.generate_tweet = AsyncMock(return_value="Test tweet")
    return provider

@pytest.fixture
async def event_engine():
    """Provide a mock EventEngine instance for testing to avoid infinite background tasks."""
    engine = MagicMock(spec=EventEngine)
    engine.add_event_listener = MagicMock()
    engine.schedule_event = MagicMock()
    engine.queue_event = MagicMock()
    engine.start = AsyncMock()
    engine.stop = AsyncMock()
    return engine

@pytest.fixture
async def agent_manager(settings, mock_memory_store, mock_vector_store, mock_llm_provider, event_engine):
    """Provide an AgentManager instance for testing with proper cleanup."""
    manager = AgentManager({
        'memory_store': mock_memory_store,
        'default_llm_provider': mock_llm_provider,
        'event_engine': event_engine,
        'settings': settings
    })
    
    yield manager 