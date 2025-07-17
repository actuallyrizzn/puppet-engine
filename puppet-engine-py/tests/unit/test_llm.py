import pytest
from src.llm.base import BaseLLMProvider, LLMResponse
from src.llm.fake_provider import FakeLLMProvider
from src.llm.openai_provider import OpenAILLMProvider

class DummyProvider(BaseLLMProvider):
    async def generate_content(self, prompt, options=None):
        return LLMResponse(content=prompt, model=self.model)
    async def generate_tweet(self, agent, prompt=""):
        return prompt

@pytest.mark.asyncio
async def test_base_llm_provider():
    provider = DummyProvider({"model": "test"})
    resp = await provider.generate_content("hi")
    assert resp.content == "hi"
    assert resp.model == "test"

@pytest.mark.asyncio
async def test_fake_llm_provider():
    provider = FakeLLMProvider({"model": "fake"})
    resp = await provider.generate_content("hello")
    assert resp.content.startswith("[FAKE LLM]")
    tweet = await provider.generate_tweet(agent=type("A", (), {"name": "Agent"})(), prompt="tweet")
    assert "FAKE TWEET" in tweet

@pytest.mark.asyncio
async def test_openai_llm_provider():
    provider = OpenAILLMProvider({"model": "openai"})
    resp = await provider.generate_content("test")
    assert "not implemented" in resp.content

@pytest.mark.asyncio
async def test_base_llm_provider_with_options():
    provider = DummyProvider({"model": "test", "max_tokens": 2048, "temperature": 0.5})
    resp = await provider.generate_content("hi", {"temperature": 0.8})
    assert resp.content == "hi"

@pytest.mark.asyncio
async def test_fake_llm_provider_with_options():
    provider = FakeLLMProvider({"model": "fake", "rate_limit_delay": 2.0})
    resp = await provider.generate_content("hello", {"max_tokens": 100})
    assert resp.content.startswith("[FAKE LLM]")
    assert resp.usage is not None

@pytest.mark.asyncio
async def test_base_llm_provider_default_config():
    provider = DummyProvider({})
    assert provider.model == "gpt-4"
    assert provider.max_tokens == 1024
    assert provider.temperature == 0.7
    assert provider.rate_limit_delay == 1.0

@pytest.mark.asyncio
async def test_fake_llm_provider_tweet_generation():
    provider = FakeLLMProvider({"model": "fake"})
    agent = type("Agent", (), {"name": "TestAgent", "personality": type("P", (), {"traits": ["kind"]})()})()
    tweet = await provider.generate_tweet(agent, "Generate a tweet")
    assert "FAKE TWEET" in tweet
    assert "TestAgent" in tweet 