import pytest
import asyncio
from datetime import datetime
from ..types import Event, Personality, StyleGuide
from ..events.router import event_router
from ..events.handlers import EVENT_TYPES
from ..agents.manager import agent_manager
from ..memory.database import db

@pytest.fixture(autouse=True)
async def setup_event_router():
    """Set up the event router before each test and clean up after."""
    await event_router.start()
    yield
    await event_router.stop()

@pytest.mark.asyncio
async def test_event_dispatch():
    """Test that events are properly dispatched to handlers."""
    events_handled = []
    
    async def test_handler(event: Event):
        events_handled.append(event)
    
    # Register a test handler
    event_router.register_handler("test.event", test_handler)
    
    # Create and dispatch a test event
    test_event = Event(
        id=1,
        type="test.event",
        payload={"test": "data"},
        timestamp=datetime.utcnow().isoformat()
    )
    
    await event_router.dispatch_event(test_event)
    
    # Wait for event processing
    await asyncio.sleep(0.1)
    
    assert len(events_handled) == 1
    assert events_handled[0].type == "test.event"
    assert events_handled[0].payload["test"] == "data"

@pytest.mark.asyncio
async def test_agent_event_handling():
    """Test that agent-specific events are handled correctly."""
    # Create an agent
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
        style_guide=style_guide
    )
    
    # Create a memory to trigger an event
    await db.add_memory(
        agent_id=agent.id,
        content="Test memory"
    )
    
    # Wait for event processing
    await asyncio.sleep(0.1)
    
    # Verify the memory was created
    memories = await db.get_agent_memories(agent_id=agent.id)
    assert len(memories) == 2  # One from agent creation, one from our test
    assert any(m["content"] == "Test memory" for m in memories)

@pytest.mark.asyncio
async def test_relationship_event_handling():
    """Test that relationship events are handled correctly."""
    # Create two agents
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
    
    # Create a relationship
    await agent_manager.add_relationship(
        agent_id=agent1.id,
        target_id=agent2.id,
        relationship_type="friend",
        strength=0.8
    )
    
    # Wait for event processing
    await asyncio.sleep(0.1)
    
    # Verify the relationship was created and logged
    memories = await db.get_agent_memories(agent_id=agent1.id)
    assert any("Created friend relationship with Agent 2" in m["content"] for m in memories)

@pytest.mark.asyncio
async def test_error_event_handling():
    """Test that error events are handled correctly."""
    # Create an agent
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
        style_guide=style_guide
    )
    
    # Create an error event
    error_event = Event(
        id=1,
        type=EVENT_TYPES["ERROR_OCCURRED"],
        payload={
            "agent_id": agent.id,
            "error_type": "test_error",
            "error_message": "This is a test error"
        },
        timestamp=datetime.utcnow().isoformat()
    )
    
    await event_router.dispatch_event(error_event)
    
    # Wait for event processing
    await asyncio.sleep(0.1)
    
    # Verify the error was logged
    memories = await db.get_agent_memories(agent_id=agent.id)
    assert any("Error occurred: test_error - This is a test error" in m["content"] for m in memories)

@pytest.mark.asyncio
async def test_concurrent_event_handling():
    """Test that events are handled correctly when dispatched concurrently."""
    events_handled = []
    
    async def test_handler(event: Event):
        events_handled.append(event)
        await asyncio.sleep(0.1)  # Simulate some processing time
    
    # Register a test handler
    event_router.register_handler("test.event", test_handler)
    
    # Create and dispatch multiple events concurrently
    events = [
        Event(
            id=i,
            type="test.event",
            payload={"index": i},
            timestamp=datetime.utcnow().isoformat()
        )
        for i in range(5)
    ]
    
    await asyncio.gather(*(event_router.dispatch_event(event) for event in events))
    
    # Wait for event processing
    await asyncio.sleep(0.6)
    
    assert len(events_handled) == 5
    assert sorted(e.payload["index"] for e in events_handled) == list(range(5)) 