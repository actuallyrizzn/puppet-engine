import pytest
from unittest.mock import patch, MagicMock
from src.llm.openai_provider import OpenAILLMProvider

def test_generate():
    provider = OpenAILLMProvider({'api_key': 'key', 'model': 'gpt-3'})
    with patch('src.llm.openai_provider.openai.ChatCompletion.create', return_value={'choices': [{'message': {'content': 'hi'}}]}):
        result = provider.generate('prompt')
        assert result == 'hi'

def test_generate_error():
    provider = OpenAILLMProvider({'api_key': 'key', 'model': 'gpt-3'})
    with patch('src.llm.openai_provider.openai.ChatCompletion.create', side_effect=Exception('fail')):
        with pytest.raises(Exception):
            provider.generate('prompt') 