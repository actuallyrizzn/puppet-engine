import pytest
from ..types import Agent, Personality, StyleGuide
from ..agents.manager import agent_manager
from ..memory.database import db

@pytest.fixture(autouse=True)
async def setup_database():
    """Set up the database before each test and clean up after."""
    await db.initialize()
    yield
    await db.close()

@pytest.mark.asyncio
async def test_create_agent():
    """Test creating a new agent."""
    personality = Personality(
        name="Test Personality",
        description="A test personality",
        traits=["friendly", "curious"]
    )
    
    style_guide = StyleGuide(
        tone="casual",
        language="english",
        quirks=["uses emojis", "talks in third person"]
    )
    
    agent = await agent_manager.create_agent(
        name="Test Agent",
        personality=personality,
        style_guide=style_guide,
        mood="happy"
    )
    
    assert agent.id is not None
    assert agent.name == "Test Agent"
    assert agent.personality.name == "Test Personality"
    assert agent.style_guide.tone == "casual"
    assert agent.mood == "happy"

@pytest.mark.asyncio
async def test_get_agent():
    """Test retrieving an agent."""
    # Create an agent first
    personality = Personality(
        name="Test Personality",
        description="A test personality",
        traits=["friendly"]
    )
    
    style_guide = StyleGuide(
        tone="casual",
        language="english"
    )
    
    created_agent = await agent_manager.create_agent(
        name="Test Agent",
        personality=personality,
        style_guide=style_guide
    )
    
    # Retrieve the agent
    retrieved_agent = await agent_manager.get_agent(created_agent.id)
    
    assert retrieved_agent is not None
    assert retrieved_agent.id == created_agent.id
    assert retrieved_agent.name == created_agent.name
    assert retrieved_agent.personality.name == created_agent.personality.name

@pytest.mark.asyncio
async def test_list_agents():
    """Test listing all agents."""
    # Create multiple agents
    personality = Personality(
        name="Test Personality",
        description="A test personality",
        traits=["friendly"]
    )
    
    style_guide = StyleGuide(
        tone="casual",
        language="english"
    )
    
    await agent_manager.create_agent(
        name="Agent 1",
        personality=personality,
        style_guide=style_guide
    )
    
    await agent_manager.create_agent(
        name="Agent 2",
        personality=personality,
        style_guide=style_guide
    )
    
    agents = await agent_manager.list_agents()
    assert len(agents) == 2
    assert any(agent.name == "Agent 1" for agent in agents)
    assert any(agent.name == "Agent 2" for agent in agents)

@pytest.mark.asyncio
async def test_update_agent_mood():
    """Test updating an agent's mood."""
    personality = Personality(
        name="Test Personality",
        description="A test personality",
        traits=["friendly"]
    )
    
    style_guide = StyleGuide(
        tone="casual",
        language="english"
    )
    
    agent = await agent_manager.create_agent(
        name="Test Agent",
        personality=personality,
        style_guide=style_guide,
        mood="neutral"
    )
    
    updated_agent = await agent_manager.update_agent_mood(agent.id, "excited")
    assert updated_agent.mood == "excited"
    
    # Verify the change persisted
    retrieved_agent = await agent_manager.get_agent(agent.id)
    assert retrieved_agent.mood == "excited"

@pytest.mark.asyncio
async def test_add_relationship():
    """Test adding a relationship between agents."""
    personality = Personality(
        name="Test Personality",
        description="A test personality",
        traits=["friendly"]
    )
    
    style_guide = StyleGuide(
        tone="casual",
        language="english"
    )
    
    agent1 = await agent_manager.create_agent(
        name="Agent 1",
        personality=personality,
        style_guide=style_guide
    )
    
    agent2 = await agent_manager.create_agent(
        name="Agent 2",
        personality=personality,
        style_guide=style_guide
    )
    
    relationship = await agent_manager.add_relationship(
        agent_id=agent1.id,
        target_id=agent2.id,
        relationship_type="friend",
        strength=0.8
    )
    
    assert relationship is not None
    assert relationship.agent_id == agent1.id
    assert relationship.target_id == agent2.id
    assert relationship.relationship_type == "friend"
    assert relationship.strength == 0.8
    
    # Verify the relationship is loaded with the agent
    retrieved_agent = await agent_manager.get_agent(agent1.id)
    assert retrieved_agent.relationships is not None
    assert len(retrieved_agent.relationships) == 1
    assert retrieved_agent.relationships[0].target_id == agent2.id 