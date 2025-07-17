import pytest
import asyncio
import logging
import traceback
from unittest.mock import AsyncMock, MagicMock
from src.core.settings import Settings
from src.memory.base import MemoryStore, VectorStore
from src.llm.base import BaseLLMProvider
from src.events.engine import EventEngine
from src.agents.agent_manager import AgentManager

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session", autouse=True)
def print_asyncio_tasks_at_end(request):
    def finalizer():
        logger.info("=== FINALIZER: Checking for running asyncio tasks at session end ===")
        try:
            loop = asyncio.get_event_loop()
            tasks = asyncio.all_tasks(loop)
            logger.info(f"FINALIZER: {len(tasks)} tasks still running.")
            for task in tasks:
                logger.info(f"Task: {task}")
                stack = task.get_stack()
                if stack:
                    logger.info(''.join(traceback.format_list(traceback.extract_stack(stack[-1]))))
        except Exception as e:
            logger.error(f"Error in finalizer: {e}")
    request.addfinalizer(finalizer)

@pytest.fixture(scope="session")
async def session_teardown():
    """Session-level fixture to handle cleanup at the end of all tests."""
    yield
    logger.info("=== SESSION TEARDOWN STARTING ===")
    
    # Get all running tasks
    try:
        tasks = asyncio.all_tasks()
        logger.info(f"Active tasks at session teardown: {len(tasks)}")
        for task in tasks:
            logger.info(f"  - {task.get_name()}: {task}")
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
    
    # Force cleanup of any remaining EventEngine instances
    try:
        # Cancel all tasks
        tasks = asyncio.all_tasks()
        for task in tasks:
            if not task.done():
                logger.info(f"Cancelling task: {task.get_name()}")
                task.cancel()
        
        # Wait for cancellation
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        logger.error(f"Error during task cleanup: {e}")
    
    logger.info("=== SESSION TEARDOWN COMPLETE ===")

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
    """Provide an AgentManager instance for testing."""
    manager = AgentManager({
        'memory_store': mock_memory_store,
        'default_llm_provider': mock_llm_provider,
        'event_engine': event_engine,
        'settings': settings
    })
    yield manager 