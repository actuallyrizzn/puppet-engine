import pytest
from marionette.agents.agent import Agent
from marionette.types import Personality, StyleGuide, Relationship, MemoryItem

def make_agent():
    return Agent(
        id=1,
        name="TestAgent",
        personality=Personality(name="Friendly", description="Nice", traits=["kind"]),
        style_guide=StyleGuide(tone="casual", language="en"),
    )

def test_update_mood():
    agent = make_agent()
    agent.update_mood((0.5, 0.2, 0.8))
    assert agent.mood == "V:0.50 A:0.20 D:0.80"

def test_add_memory():
    agent = make_agent()
    mem = MemoryItem(id=1, agent_id=1, content="hi", timestamp="2024-01-01T00:00:00Z")
    agent.add_memory(mem)
    assert agent.memories[0].content == "hi"

def test_add_relationship():
    agent = make_agent()
    rel = Relationship(agent_id=1, target_id=2, relationship_type="friend", strength=1.0)
    agent.add_relationship(rel)
    assert agent.relationships[0].target_id == 2

def test_system_prompt():
    agent = make_agent()
    prompt = agent.system_prompt()
    assert "TestAgent" in prompt and "Friendly" in prompt and "casual" in prompt 