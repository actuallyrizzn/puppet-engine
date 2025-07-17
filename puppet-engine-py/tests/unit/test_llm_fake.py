import pytest
from src.llm.fake_provider import FakeLLMProvider

@pytest.mark.asyncio
async def test_generate_content():
    provider = FakeLLMProvider({'model': 'fake'})
    result = await provider.generate_content('prompt')
    assert isinstance(result.content, str)
    assert 'FAKE LLM' in result.content

@pytest.mark.asyncio
async def test_generate_tweet():
    provider = FakeLLMProvider({'model': 'fake'})
    from unittest.mock import MagicMock
    agent = MagicMock(name='test_agent')
    result = await provider.generate_tweet(agent, 'prompt')
    assert 'test_agent' in result 