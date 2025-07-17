import pytest
from unittest.mock import MagicMock
from src.llm.base import BaseLLMProvider

class DummyProvider(BaseLLMProvider):
    def generate(self, prompt, **kwargs):
        return 'response'

def test_generate():
    provider = DummyProvider({'model': 'test'})
    assert provider.generate('prompt') == 'response'

def test_config():
    provider = DummyProvider({'model': 'test'})
    assert provider.config['model'] == 'test' 