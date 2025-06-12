import pytest
from unittest.mock import AsyncMock, patch
from ..llm.client import LLMClient, llm_client
from ..types import Event
from ..events.handlers import EVENT_TYPES

@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing."""
    with patch("openai.AsyncOpenAI") as mock:
        mock_client = AsyncMock()
        mock.return_value = mock_client
        yield mock_client

@pytest.mark.asyncio
async def test_generate_completion(mock_openai):
    """Test generating a completion."""
    # Mock the OpenAI response
    mock_openai.chat.completions.create.return_value.choices = [
        AsyncMock(message=AsyncMock(content="Test response"))
    ]
    
    response = await llm_client.generate_completion(
        prompt="Test prompt",
        system_prompt="Test system prompt"
    )
    
    assert response == "Test response"
    mock_openai.chat.completions.create.assert_called_once()
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    assert call_kwargs["messages"] == [
        {"role": "system", "content": "Test system prompt"},
        {"role": "user", "content": "Test prompt"}
    ]

@pytest.mark.asyncio
async def test_generate_agent_prompt():
    """Test generating an agent prompt."""
    personality = {
        "name": "Test Personality",
        "description": "A test personality",
        "traits": ["friendly", "curious"]
    }
    
    style_guide = {
        "tone": "casual",
        "language": "english",
        "quirks": ["uses emojis", "talks in third person"]
    }
    
    prompt = await llm_client.generate_agent_prompt(
        agent_name="Test Agent",
        personality=personality,
        style_guide=style_guide,
        context="Test context"
    )
    
    assert "Test Agent" in prompt
    assert "Test Personality" in prompt
    assert "friendly, curious" in prompt
    assert "casual" in prompt
    assert "uses emojis, talks in third person" in prompt
    assert "Test context" in prompt

@pytest.mark.asyncio
async def test_analyze_sentiment(mock_openai):
    """Test sentiment analysis."""
    # Mock the OpenAI response
    mock_openai.chat.completions.create.return_value.choices = [
        AsyncMock(message=AsyncMock(content="""
positivity: 0.8
energy: 0.6
formality: 0.3
"""))
    ]
    
    scores = await llm_client.analyze_sentiment("Test text")
    
    assert scores["positivity"] == 0.8
    assert scores["energy"] == 0.6
    assert scores["formality"] == 0.3

@pytest.mark.asyncio
async def test_generate_memory_summary(mock_openai):
    """Test generating a memory summary."""
    # Mock the OpenAI response
    mock_openai.chat.completions.create.return_value.choices = [
        AsyncMock(message=AsyncMock(content="Test summary"))
    ]
    
    memories = [
        {
            "content": "Memory 1",
            "timestamp": "2024-01-01T00:00:00"
        },
        {
            "content": "Memory 2",
            "timestamp": "2024-01-02T00:00:00"
        }
    ]
    
    summary = await llm_client.generate_memory_summary(memories)
    
    assert summary == "Test summary"
    mock_openai.chat.completions.create.assert_called_once()
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    assert "Memory 1" in call_kwargs["messages"][1]["content"]
    assert "Memory 2" in call_kwargs["messages"][1]["content"]

@pytest.mark.asyncio
async def test_error_handling(mock_openai):
    """Test error handling and retry logic."""
    # Mock OpenAI to raise an error
    mock_openai.chat.completions.create.side_effect = Exception("Test error")
    
    with pytest.raises(Exception) as exc_info:
        await llm_client.generate_completion("Test prompt")
    
    assert str(exc_info.value) == "Test error"
    assert mock_openai.chat.completions.create.call_count == 3  # Max retries

@pytest.mark.asyncio
async def test_empty_memory_summary():
    """Test generating a summary with no memories."""
    summary = await llm_client.generate_memory_summary([])
    assert summary == "No recent memories to summarize." 