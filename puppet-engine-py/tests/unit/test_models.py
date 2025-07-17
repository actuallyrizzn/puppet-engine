from src.core.models import Agent, Personality, MemoryType, MemoryItem, Event, Tweet, LLMResponse
from datetime import datetime

def test_personality_strip():
    p = Personality(traits=["  kind  ", "smart"], values=[" honest ", "brave"], interests=["ai ", "trading"])
    assert p.traits == ["kind", "smart"]
    assert p.values == ["honest", "brave"]
    assert p.interests == ["ai", "trading"]

def test_agent_model():
    agent = Agent(id="agent1", name="Test Agent")
    assert agent.id == "agent1"
    assert agent.name == "Test Agent"
    assert agent.is_active

def test_memory_item():
    m = MemoryItem(agent_id="agent1", type=MemoryType.CORE, content="test")
    assert m.type == MemoryType.CORE
    assert m.content == "test"
    assert isinstance(m.timestamp, datetime)

def test_event_model():
    event = Event(type="test_event", agent_id="agent1", data={"key": "value"})
    assert event.type == "test_event"
    assert event.agent_id == "agent1"
    assert event.data["key"] == "value"

def test_tweet_model():
    tweet = Tweet(text="Hello world", agent_id="agent1")
    assert tweet.text == "Hello world"
    assert tweet.agent_id == "agent1"

def test_llm_response_model():
    response = LLMResponse(content="test response", model="gpt-4")
    assert response.content == "test response"
    assert response.model == "gpt-4" 