import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from ..agents.runtime import AgentRuntime
from ..types import Agent, MemoryItem, Relationship, Personality, StyleGuide
from ..events.handlers import EVENT_TYPES

@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    with patch("marionette.llm.client.llm_client") as mock:
        mock.analyze_sentiment.return_value = {
            "positivity": 0.8,
            "energy": 0.6,
            "formality": 0.3
        }
        mock.generate_memory_summary.return_value = "Test memory summary"
        mock.generate_agent_prompt.return_value = "Test prompt"
        mock.generate_completion.return_value = "Test response"
        yield mock

@pytest.fixture
def mock_event_router():
    """Mock event router for testing."""
    with patch("marionette.events.router.event_router") as mock:
        mock.dispatch_event = AsyncMock()
        yield mock

@pytest.fixture
def test_agent():
    """Create a test agent."""
    return Agent(
        id="test-agent-1",
        name="Test Agent",
        personality=Personality(
            name="Test Personality",
            description="A test personality",
            traits=["friendly", "curious"]
        ),
        style_guide=StyleGuide(
            tone="casual",
            language="english",
            quirks=["uses emojis", "talks in third person"]
        ),
        behavior_profile={
            "posting_frequency": 0.5,
            "interaction_style": "friendly"
        }
    )

@pytest.fixture
def agent_runtime(test_agent, mock_llm_client, mock_event_router):
    """Create an agent runtime instance."""
    return AgentRuntime(test_agent)

@pytest.mark.asyncio
async def test_process_memory(agent_runtime, mock_llm_client, mock_event_router):
    """Test processing a new memory."""
    memory = MemoryItem(
        id="test-memory-1",
        agent_id="test-agent-1",
        content="Test memory content",
        timestamp=datetime.utcnow()
    )
    
    await agent_runtime.process_memory(memory)
    
    # Check mood update
    mood = agent_runtime.get_mood()
    assert mood["positivity"] == 0.59  # 0.5 * 0.7 + 0.8 * 0.3
    assert mood["energy"] == 0.53  # 0.5 * 0.7 + 0.6 * 0.3
    assert mood["formality"] == 0.44  # 0.5 * 0.7 + 0.3 * 0.3
    
    # Check event dispatch
    mock_event_router.dispatch_event.assert_called_once()
    event = mock_event_router.dispatch_event.call_args[0][0]
    assert event.type == EVENT_TYPES["MOOD_CHANGED"]
    assert event.agent_id == "test-agent-1"

@pytest.mark.asyncio
async def test_generate_response(agent_runtime, mock_llm_client):
    """Test generating a response."""
    memories = [
        MemoryItem(
            id="test-memory-1",
            agent_id="test-agent-1",
            content="Test memory 1",
            timestamp=datetime.utcnow()
        ),
        MemoryItem(
            id="test-memory-2",
            agent_id="test-agent-1",
            content="Test memory 2",
            timestamp=datetime.utcnow()
        )
    ]
    
    response = await agent_runtime.generate_response("Test context", memories)
    
    assert response == "Test response"
    mock_llm_client.generate_memory_summary.assert_called_once()
    mock_llm_client.generate_agent_prompt.assert_called_once()
    mock_llm_client.generate_completion.assert_called_once()

@pytest.mark.asyncio
async def test_process_relationship(agent_runtime, mock_event_router):
    """Test processing a new relationship."""
    relationship = Relationship(
        id="test-relationship-1",
        agent_id="test-agent-1",
        target_id="test-agent-2",
        type="friend",
        strength=0.8
    )
    
    await agent_runtime.process_relationship(relationship)
    
    # Check relationship added
    assert relationship in agent_runtime.agent.relationships
    
    # Check event dispatch
    mock_event_router.dispatch_event.assert_called_once()
    event = mock_event_router.dispatch_event.call_args[0][0]
    assert event.type == EVENT_TYPES["RELATIONSHIP_CREATED"]
    assert event.agent_id == "test-agent-1"

def test_get_interaction_frequency(agent_runtime):
    """Test interaction frequency calculation."""
    # Set last interaction to 1 day ago
    agent_runtime.last_interaction = datetime.utcnow() - timedelta(days=1)
    assert agent_runtime.get_interaction_frequency() == 1.0
    
    # Set last interaction to 2 days ago
    agent_runtime.last_interaction = datetime.utcnow() - timedelta(days=2)
    assert agent_runtime.get_interaction_frequency() == 0.5

@pytest.mark.asyncio
async def test_update_behavior_profile(agent_runtime, mock_event_router):
    """Test updating behavior profile."""
    new_profile = {
        "posting_frequency": 0.8,
        "interaction_style": "formal"
    }
    
    await agent_runtime.update_behavior_profile(new_profile)
    
    # Check profile update
    assert agent_runtime.agent.behavior_profile["posting_frequency"] == 0.8
    assert agent_runtime.agent.behavior_profile["interaction_style"] == "formal"
    
    # Check event dispatch
    mock_event_router.dispatch_event.assert_called_once()
    event = mock_event_router.dispatch_event.call_args[0][0]
    assert event.type == EVENT_TYPES["PROFILE_UPDATED"]
    assert event.agent_id == "test-agent-1" 