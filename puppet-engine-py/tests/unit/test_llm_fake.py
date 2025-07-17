import pytest
from src.llm.fake_provider import FakeLLMProvider

def test_generate():
    provider = FakeLLMProvider({'model': 'fake'})
    result = provider.generate('prompt')
    assert isinstance(result, str) 