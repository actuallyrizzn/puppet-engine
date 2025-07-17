import pytest
from unittest.mock import MagicMock
from src.llm.base import BaseLLMProvider, LLMResponse

class DummyProvider(BaseLLMProvider):
    async def generate_content(self, prompt, options=None):
        return LLMResponse(content='response', model='test')
    
    async def generate_tweet(self, agent, prompt=""):
        return 'tweet response'

@pytest.mark.asyncio
async def test_generate_content():
    provider = DummyProvider({'model': 'test'})
    result = await provider.generate_content('prompt')
    assert result.content == 'response'

@pytest.mark.asyncio
async def test_generate_tweet():
    provider = DummyProvider({'model': 'test'})
    result = await provider.generate_tweet(MagicMock(), 'prompt')
    assert result == 'tweet response'

def test_config():
    provider = DummyProvider({'model': 'test'})
    assert provider.config['model'] == 'test' 