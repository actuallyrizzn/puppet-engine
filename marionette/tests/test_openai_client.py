import pytest
from marionette.llm.openai_client import OpenAIClient
import openai
import asyncio

class DummyResp:
    def __getitem__(self, key):
        return [{"message": {"content": "hello!"}}]

@pytest.mark.asyncio
async def test_chat(monkeypatch):
    async def fake_acreate(*args, **kwargs):
        return DummyResp()
    monkeypatch.setattr(openai.ChatCompletion, "acreate", fake_acreate)
    client = OpenAIClient(api_key="test")
    result = await client.chat([{"role": "user", "content": "hi"}])
    assert result == "hello!" 