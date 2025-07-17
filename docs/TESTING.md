# Testing Guide

## Overview

Puppet Engine includes a comprehensive test suite covering unit tests, integration tests, and end-to-end tests. The testing framework is built on pytest with async support and extensive mocking capabilities.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests for individual components
│   ├── test_agents.py       # Agent management tests
│   ├── test_api.py          # API server tests
│   ├── test_events.py       # Event engine tests
│   ├── test_llm.py          # LLM provider tests
│   ├── test_memory.py       # Memory store tests
│   ├── test_solana.py       # Solana trading tests
│   └── test_twitter.py      # Twitter client tests
├── integration/             # Integration tests
│   ├── test_agent_workflow.py
│   ├── test_api_memory.py
│   └── test_trading_flow.py
└── e2e/                     # End-to-end tests
    └── test_e2e_flow.py
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py

# Run specific test function
pytest tests/unit/test_agents.py::test_agent_creation
```

### Test Categories

```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run only end-to-end tests
pytest tests/e2e/

# Run tests by marker
pytest -m "unit"
pytest -m "integration"
pytest -m "e2e"
```

### Test Configuration

The test configuration is defined in `pytest.ini`:

```ini
[tool:pytest]
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    async: Async tests
asyncio_mode = auto
```

## Test Fixtures

### Core Fixtures

The `conftest.py` file provides shared fixtures for all tests:

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.core.settings import Settings
from src.memory.base import MemoryStore
from src.llm.base import LLMProvider

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def settings():
    """Provide test settings."""
    return Settings(
        database_url="sqlite:///:memory:",
        log_level="DEBUG",
        enable_metrics=False
    )

@pytest.fixture
def mock_memory_store():
    """Provide a mock memory store."""
    store = AsyncMock(spec=MemoryStore)
    store.add_memory.return_value = "mem_123"
    store.search_memories.return_value = []
    return store

@pytest.fixture
def mock_llm_provider():
    """Provide a mock LLM provider."""
    provider = AsyncMock(spec=LLMProvider)
    provider.generate_content.return_value = "Generated content"
    provider.generate_tweet.return_value = "Generated tweet"
    return provider

@pytest.fixture
def mock_twitter_client():
    """Provide a mock Twitter client."""
    client = AsyncMock()
    client.post_tweet.return_value = "tweet_123"
    client.get_mentions.return_value = []
    return client

@pytest.fixture
def mock_solana_trader():
    """Provide a mock Solana trader."""
    trader = AsyncMock()
    trader.execute_trade.return_value = {
        "trade_id": "trade_123",
        "status": "success"
    }
    return trader
```

### Agent Fixtures

```python
@pytest.fixture
def sample_agent_config():
    """Provide a sample agent configuration."""
    return {
        "id": "test-agent",
        "name": "Test Agent",
        "description": "A test agent",
        "personality": {
            "traits": ["curious", "helpful"],
            "values": ["knowledge", "community"],
            "speaking_style": "Friendly and informative",
            "interests": ["technology", "AI"]
        },
        "style_guide": {
            "voice": "first_person",
            "tone": "casual",
            "formatting": {
                "uses_hashtags": True,
                "uses_emojis": True
            }
        },
        "behavior": {
            "post_frequency": {
                "min_hours_between_posts": 1,
                "max_hours_between_posts": 4
            },
            "interaction_patterns": {
                "reply_probability": 0.8,
                "like_probability": 0.7
            }
        }
    }

@pytest.fixture
def agent_manager(settings, mock_memory_store, mock_llm_provider):
    """Provide an agent manager with mocked dependencies."""
    from src.agents.agent_manager import AgentManager
    
    config = {
        'memory_store': mock_memory_store,
        'default_llm_provider': mock_llm_provider,
        'event_engine': MagicMock()
    }
    
    return AgentManager(config)
```

## Unit Tests

### Agent Tests

```python
import pytest
from src.agents.agent_manager import AgentManager
from src.core.models import AgentConfig

class TestAgentManager:
    """Test agent management functionality."""
    
    @pytest.mark.asyncio
    async def test_agent_creation(self, agent_manager, sample_agent_config):
        """Test creating a new agent."""
        agent_id = await agent_manager.create_agent(sample_agent_config)
        
        assert agent_id == "test-agent"
        assert "test-agent" in agent_manager.agents
        
        agent = agent_manager.agents["test-agent"]
        assert agent.name == "Test Agent"
        assert agent.personality.traits == ["curious", "helpful"]
    
    @pytest.mark.asyncio
    async def test_agent_posting(self, agent_manager, sample_agent_config, mock_twitter_client):
        """Test agent posting functionality."""
        agent_id = await agent_manager.create_agent(sample_agent_config)
        agent_manager.twitter_client = mock_twitter_client
        
        post_id = await agent_manager.trigger_post(agent_id, {"topic": "AI"})
        
        assert post_id == "tweet_123"
        mock_twitter_client.post_tweet.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_agent_memory_management(self, agent_manager, sample_agent_config, mock_memory_store):
        """Test agent memory operations."""
        agent_id = await agent_manager.create_agent(sample_agent_config)
        
        memory_id = await agent_manager.add_memory(agent_id, "Test memory", "recent")
        
        assert memory_id == "mem_123"
        mock_memory_store.add_memory.assert_called_once_with(
            agent_id, 
            pytest.approx({"content": "Test memory", "type": "recent"})
        )
```

### LLM Provider Tests

```python
import pytest
from src.llm.openai_provider import OpenAIProvider
from src.llm.fake_provider import FakeLLMProvider

class TestLLMProviders:
    """Test LLM provider implementations."""
    
    @pytest.mark.asyncio
    async def test_openai_provider(self, settings):
        """Test OpenAI provider functionality."""
        provider = OpenAIProvider(settings)
        
        # Mock the OpenAI API call
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value.choices[0].message.content = "Test response"
            
            response = await provider.generate_content("Test prompt", {})
            
            assert response == "Test response"
    
    @pytest.mark.asyncio
    async def test_fake_provider(self):
        """Test fake provider for testing."""
        provider = FakeLLMProvider()
        
        response = await provider.generate_content("Test prompt", {})
        
        assert "Test prompt" in response
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_provider_error_handling(self, settings):
        """Test error handling in LLM providers."""
        provider = OpenAIProvider(settings)
        
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                await provider.generate_content("Test prompt", {})
```

### Memory Store Tests

```python
import pytest
from src.memory.sqlite_store import SQLiteStore
from src.core.models import Memory

class TestMemoryStore:
    """Test memory store functionality."""
    
    @pytest.mark.asyncio
    async def test_memory_creation(self, settings):
        """Test creating memory entries."""
        store = SQLiteStore(settings)
        await store.initialize()
        
        memory = Memory(
            content="Test memory",
            type="recent",
            metadata={"source": "test"}
        )
        
        memory_id = await store.add_memory("test-agent", memory)
        
        assert memory_id is not None
        assert len(memory_id) > 0
    
    @pytest.mark.asyncio
    async def test_memory_search(self, settings):
        """Test memory search functionality."""
        store = SQLiteStore(settings)
        await store.initialize()
        
        # Add test memories
        memory1 = Memory(content="AI is amazing", type="core")
        memory2 = Memory(content="Blockchain technology", type="recent")
        
        await store.add_memory("test-agent", memory1)
        await store.add_memory("test-agent", memory2)
        
        # Search for AI-related memories
        results = await store.search_memories("test-agent", "artificial intelligence", limit=5)
        
        assert len(results) > 0
        assert any("AI" in result.content for result in results)
    
    @pytest.mark.asyncio
    async def test_memory_deletion(self, settings):
        """Test memory deletion."""
        store = SQLiteStore(settings)
        await store.initialize()
        
        memory = Memory(content="Test memory", type="recent")
        memory_id = await store.add_memory("test-agent", memory)
        
        # Verify memory exists
        memories = await store.get_memories("test-agent", limit=10)
        assert any(m.id == memory_id for m in memories)
        
        # Delete memory
        await store.delete_memory("test-agent", memory_id)
        
        # Verify memory is deleted
        memories = await store.get_memories("test-agent", limit=10)
        assert not any(m.id == memory_id for m in memories)
```

## Integration Tests

### Agent Workflow Tests

```python
import pytest
from src.agents.agent_manager import AgentManager
from src.events.engine import EventEngine
from src.memory.sqlite_store import SQLiteStore

class TestAgentWorkflow:
    """Test complete agent workflows."""
    
    @pytest.mark.asyncio
    async def test_agent_lifecycle(self, settings):
        """Test complete agent lifecycle."""
        # Initialize components
        memory_store = SQLiteStore(settings)
        await memory_store.initialize()
        
        event_engine = EventEngine()
        await event_engine.start()
        
        agent_manager = AgentManager({
            'memory_store': memory_store,
            'default_llm_provider': FakeLLMProvider(),
            'event_engine': event_engine
        })
        
        # Create agent
        agent_config = {
            "id": "workflow-test-agent",
            "name": "Workflow Test Agent",
            "personality": {
                "traits": ["curious"],
                "values": ["knowledge"],
                "speaking_style": "Friendly",
                "interests": ["technology"]
            },
            "behavior": {
                "post_frequency": {
                    "min_hours_between_posts": 0.01,  # Very frequent for testing
                    "max_hours_between_posts": 0.02
                }
            }
        }
        
        agent_id = await agent_manager.create_agent(agent_config)
        
        # Start agent
        await agent_manager.start_agents()
        
        # Wait for some activity
        await asyncio.sleep(0.1)
        
        # Verify agent is active
        assert agent_id in agent_manager.agents
        assert agent_manager.agents[agent_id].is_active
        
        # Stop agent
        await agent_manager.stop_agents()
        await event_engine.stop()
        
        # Verify agent is stopped
        assert not agent_manager.agents[agent_id].is_active
    
    @pytest.mark.asyncio
    async def test_agent_memory_integration(self, settings):
        """Test agent memory integration."""
        memory_store = SQLiteStore(settings)
        await memory_store.initialize()
        
        agent_manager = AgentManager({
            'memory_store': memory_store,
            'default_llm_provider': FakeLLMProvider(),
            'event_engine': MagicMock()
        })
        
        # Create agent with initial memory
        agent_config = {
            "id": "memory-test-agent",
            "name": "Memory Test Agent",
            "initial_memory": {
                "core_memories": ["I am a test agent"],
                "recent_events": ["Just started testing"]
            }
        }
        
        agent_id = await agent_manager.create_agent(agent_config)
        
        # Verify initial memories are loaded
        memories = await memory_store.get_memories(agent_id, limit=10)
        assert len(memories) >= 2
        
        # Add new memory
        await agent_manager.add_memory(agent_id, "New test memory", "recent")
        
        # Verify new memory is added
        memories = await memory_store.get_memories(agent_id, limit=10)
        assert len(memories) >= 3
        assert any("New test memory" in m.content for m in memories)
```

### API Integration Tests

```python
import pytest
from fastapi.testclient import TestClient
from src.api.server import APIServer

class TestAPIIntegration:
    """Test API integration."""
    
    @pytest.fixture
    def api_client(self, agent_manager, mock_memory_store):
        """Provide API test client."""
        api_server = APIServer(agent_manager, mock_memory_store)
        return TestClient(api_server.app)
    
    def test_health_endpoint(self, api_client):
        """Test health check endpoint."""
        response = api_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "healthy"
    
    def test_agents_endpoint(self, api_client):
        """Test agents endpoint."""
        response = api_client.get("/agents")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "agents" in data["data"]
    
    def test_agent_creation_via_api(self, api_client, sample_agent_config):
        """Test agent creation via API."""
        response = api_client.post("/agents", json=sample_agent_config)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["agent_id"] == "test-agent"
    
    def test_memory_operations_via_api(self, api_client, mock_memory_store):
        """Test memory operations via API."""
        # Add memory
        memory_data = {
            "type": "recent",
            "content": "API test memory"
        }
        
        response = api_client.post("/memory/test-agent", json=memory_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "memory_id" in data["data"]
        
        # Get memories
        response = api_client.get("/memory/test-agent")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "memories" in data["data"]
```

## End-to-End Tests

### Complete System Tests

```python
import pytest
import asyncio
from src.main import create_app
from src.agents.agent_manager import AgentManager
from src.events.engine import EventEngine

class TestE2EFlow:
    """Test complete end-to-end workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_system_startup(self, settings):
        """Test complete system startup and shutdown."""
        # Initialize all components
        app = create_app(settings)
        
        # Start the system
        await app.startup()
        
        # Verify all components are running
        assert app.agent_manager is not None
        assert app.event_engine is not None
        assert app.memory_store is not None
        
        # Create a test agent
        agent_config = {
            "id": "e2e-test-agent",
            "name": "E2E Test Agent",
            "personality": {
                "traits": ["curious"],
                "values": ["knowledge"],
                "speaking_style": "Friendly",
                "interests": ["technology"]
            }
        }
        
        agent_id = await app.agent_manager.create_agent(agent_config)
        
        # Verify agent is created and active
        assert agent_id in app.agent_manager.agents
        assert app.agent_manager.agents[agent_id].is_active
        
        # Shutdown the system
        await app.shutdown()
        
        # Verify clean shutdown
        assert not app.agent_manager.agents[agent_id].is_active
    
    @pytest.mark.asyncio
    async def test_agent_posting_workflow(self, settings):
        """Test complete agent posting workflow."""
        app = create_app(settings)
        await app.startup()
        
        # Create agent with frequent posting
        agent_config = {
            "id": "posting-test-agent",
            "name": "Posting Test Agent",
            "personality": {
                "traits": ["enthusiastic"],
                "values": ["sharing"],
                "speaking_style": "Excited and informative",
                "interests": ["technology"]
            },
            "behavior": {
                "post_frequency": {
                    "min_hours_between_posts": 0.01,
                    "max_hours_between_posts": 0.02
                }
            }
        }
        
        agent_id = await app.agent_manager.create_agent(agent_config)
        
        # Wait for posting activity
        await asyncio.sleep(0.2)
        
        # Verify posting occurred
        memories = await app.memory_store.get_memories(agent_id, limit=10)
        assert len(memories) > 0
        
        await app.shutdown()
    
    @pytest.mark.asyncio
    async def test_trading_workflow(self, settings):
        """Test complete trading workflow."""
        app = create_app(settings)
        await app.startup()
        
        # Create agent with trading enabled
        agent_config = {
            "id": "trading-test-agent",
            "name": "Trading Test Agent",
            "solana_integration": {
                "trading_enabled": True,
                "wallet_address": "test_wallet",
                "private_key": "test_key"
            },
            "behavior": {
                "trading_behavior": {
                    "trading_frequency": {
                        "min_hours_between_trades": 0.01,
                        "max_hours_between_trades": 0.02
                    }
                }
            }
        }
        
        agent_id = await app.agent_manager.create_agent(agent_config)
        
        # Wait for trading activity
        await asyncio.sleep(0.2)
        
        # Verify trading occurred
        memories = await app.memory_store.get_memories(agent_id, limit=10)
        trading_memories = [m for m in memories if "trade" in m.content.lower()]
        assert len(trading_memories) > 0
        
        await app.shutdown()
```

## Mocking Strategies

### External API Mocking

```python
import pytest
from unittest.mock import patch, AsyncMock
import aiohttp

class TestExternalAPIs:
    """Test external API interactions."""
    
    @pytest.mark.asyncio
    async def test_twitter_api_mocking(self):
        """Test Twitter API mocking."""
        with patch('tweepy.AsyncClient') as mock_client:
            mock_client.return_value.create_tweet.return_value.data = {
                'id': '123456789',
                'text': 'Test tweet'
            }
            
            # Test Twitter client
            from src.twitter.client import TwitterClient
            client = TwitterClient({})
            
            result = await client.post_tweet("Test tweet")
            assert result == "123456789"
    
    @pytest.mark.asyncio
    async def test_openai_api_mocking(self):
        """Test OpenAI API mocking."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value.choices[0].message.content = "Mocked response"
            
            from src.llm.openai_provider import OpenAIProvider
            provider = OpenAIProvider(Settings())
            
            response = await provider.generate_content("Test prompt", {})
            assert response == "Mocked response"
    
    @pytest.mark.asyncio
    async def test_solana_api_mocking(self):
        """Test Solana API mocking."""
        with patch('solana.rpc.async_api.AsyncClient') as mock_client:
            mock_client.return_value.get_balance.return_value.value = 1000000000  # 1 SOL
            
            from src.solana.wallet import SolanaWallet
            wallet = SolanaWallet("test_key", "test_url")
            
            balance = await wallet.get_balance()
            assert balance == 1.0
```

### Database Mocking

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

class TestDatabaseMocking:
    """Test database mocking strategies."""
    
    @pytest.mark.asyncio
    async def test_sqlite_memory_database(self, settings):
        """Test using in-memory SQLite for testing."""
        # Use in-memory database
        settings.database_url = "sqlite:///:memory:"
        
        from src.memory.sqlite_store import SQLiteStore
        store = SQLiteStore(settings)
        await store.initialize()
        
        # Test operations
        memory = Memory(content="Test memory", type="recent")
        memory_id = await store.add_memory("test-agent", memory)
        
        assert memory_id is not None
        
        memories = await store.get_memories("test-agent", limit=10)
        assert len(memories) == 1
        assert memories[0].content == "Test memory"
    
    @pytest.mark.asyncio
    async def test_mock_memory_store(self, mock_memory_store):
        """Test using mock memory store."""
        memory = Memory(content="Test memory", type="recent")
        
        memory_id = await mock_memory_store.add_memory("test-agent", memory)
        assert memory_id == "mem_123"
        
        mock_memory_store.add_memory.assert_called_once()
```

## Performance Testing

### Load Testing

```python
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

class TestPerformance:
    """Test system performance."""
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self, agent_manager, sample_agent_config):
        """Test concurrent agent operations."""
        # Create multiple agents
        agent_ids = []
        for i in range(10):
            config = sample_agent_config.copy()
            config["id"] = f"perf-test-agent-{i}"
            agent_id = await agent_manager.create_agent(config)
            agent_ids.append(agent_id)
        
        # Perform concurrent operations
        async def concurrent_operation(agent_id):
            await agent_manager.add_memory(agent_id, f"Memory for {agent_id}", "recent")
            return await agent_manager.get_memories(agent_id, limit=5)
        
        start_time = time.time()
        
        # Run concurrent operations
        tasks = [concurrent_operation(agent_id) for agent_id in agent_ids]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        
        # Verify results
        assert len(results) == 10
        assert end_time - start_time < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.asyncio
    async def test_memory_search_performance(self, settings):
        """Test memory search performance."""
        from src.memory.sqlite_store import SQLiteStore
        
        store = SQLiteStore(settings)
        await store.initialize()
        
        # Add many memories
        for i in range(1000):
            memory = Memory(
                content=f"Memory {i} about technology and AI",
                type="recent",
                metadata={"index": i}
            )
            await store.add_memory("test-agent", memory)
        
        # Test search performance
        start_time = time.time()
        
        results = await store.search_memories("test-agent", "artificial intelligence", limit=10)
        
        end_time = time.time()
        
        # Verify performance
        assert len(results) > 0
        assert end_time - start_time < 1.0  # Should complete within 1 second
```

## Test Data Management

### Test Data Fixtures

```python
import pytest
import json
import os

@pytest.fixture
def test_data_dir():
    """Provide test data directory."""
    return os.path.join(os.path.dirname(__file__), "test_data")

@pytest.fixture
def sample_tweets(test_data_dir):
    """Load sample tweets for testing."""
    with open(os.path.join(test_data_dir, "sample_tweets.json")) as f:
        return json.load(f)

@pytest.fixture
def sample_memories(test_data_dir):
    """Load sample memories for testing."""
    with open(os.path.join(test_data_dir, "sample_memories.json")) as f:
        return json.load(f)

@pytest.fixture
def agent_configs(test_data_dir):
    """Load sample agent configurations."""
    with open(os.path.join(test_data_dir, "agent_configs.json")) as f:
        return json.load(f)
```

### Test Data Cleanup

```python
import pytest
import tempfile
import shutil

@pytest.fixture
def temp_database():
    """Provide temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    yield db_path
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up test files after each test."""
    yield
    
    # Cleanup any test files
    test_files = [
        "test.db",
        "test.log",
        "coverage.xml"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
```

## Continuous Integration

### GitHub Actions Configuration

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov pytest-mock
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

## Best Practices

### Test Organization

1. **Group Related Tests**: Use classes to group related test methods
2. **Descriptive Names**: Use descriptive test method names
3. **Arrange-Act-Assert**: Follow the AAA pattern in test methods
4. **One Assertion Per Test**: Keep tests focused on a single behavior

### Test Data

1. **Use Fixtures**: Create reusable test data with fixtures
2. **Minimal Data**: Use only the data necessary for the test
3. **Realistic Data**: Use realistic but minimal test data
4. **Cleanup**: Always clean up test data after tests

### Async Testing

1. **Use pytest-asyncio**: Mark async tests with `@pytest.mark.asyncio`
2. **Proper Event Loops**: Use the event_loop fixture for async tests
3. **Timeout Handling**: Add timeouts to prevent hanging tests
4. **Concurrent Testing**: Test concurrent operations when relevant

### Mocking

1. **Mock External Dependencies**: Mock external APIs and services
2. **Use Realistic Mocks**: Make mocks behave like real implementations
3. **Verify Interactions**: Verify that mocks are called correctly
4. **Minimal Mocking**: Only mock what's necessary

### Performance

1. **Measure Performance**: Include performance tests for critical paths
2. **Set Benchmarks**: Establish performance benchmarks
3. **Monitor Regressions**: Track performance over time
4. **Optimize Tests**: Keep tests fast and efficient

## Troubleshooting

### Common Issues

1. **Hanging Tests**: Add timeouts and proper cleanup
2. **Async Issues**: Ensure proper async/await usage
3. **Database Conflicts**: Use in-memory databases for tests
4. **Resource Leaks**: Clean up resources in fixtures

### Debugging Tips

1. **Use pytest -s**: Show print statements during test execution
2. **Use pytest -x**: Stop on first failure
3. **Use pytest --pdb**: Drop into debugger on failures
4. **Use pytest --lf**: Run only the last failed tests

### Test Maintenance

1. **Regular Review**: Review and update tests regularly
2. **Remove Obsolete Tests**: Remove tests for removed functionality
3. **Update Mocks**: Update mocks when APIs change
4. **Performance Monitoring**: Monitor test suite performance 