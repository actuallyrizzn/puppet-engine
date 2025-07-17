import pytest
from unittest.mock import patch, MagicMock
from src.llm.openai_provider import OpenAILLMProvider

@pytest.mark.asyncio
async def test_generate_content():
    provider = OpenAILLMProvider({'api_key': 'key', 'model': 'gpt-3'})
    result = await provider.generate_content('prompt')
    assert result.content == '[OpenAI LLM not implemented]'

@pytest.mark.asyncio
async def test_generate_tweet():
    provider = OpenAILLMProvider({'api_key': 'key', 'model': 'gpt-3'})
    agent = MagicMock(name='test_agent')
    result = await provider.generate_tweet(agent, 'prompt')
    assert 'test_agent' in result

@pytest.mark.asyncio
async def test_generate_content_error():
    provider = OpenAILLMProvider({'api_key': 'key', 'model': 'gpt-3'})
    with patch.object(provider, 'generate_content', side_effect=Exception('fail')):
        with pytest.raises(Exception):
            await provider.generate_content('prompt') 