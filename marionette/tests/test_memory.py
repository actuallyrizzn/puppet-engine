import pytest
import asyncio
from marionette.memory import dao
from marionette.types import MemoryItem, Relationship
import os
from datetime import datetime
from ..memory.database import db, SQLiteWriteQueue
from ..agents.manager import agent_manager
from ..types import Personality, StyleGuide

@pytest.fixture(autouse=True)
async def setup_database():
    """Set up the database before each test and clean up after."""
    await db.initialize()
    yield
    await db.close()

@pytest.mark.asyncio
async def test_memory_dao(tmp_path):
    # Use a temp DB file
    dao.DB_PATH = str(tmp_path / "test.db")
    await dao.init_db()

    mem = MemoryItem(id=1, agent_id=1, content="test", timestamp="2024-01-01T00:00:00Z")
    await dao.insert_memory(mem)
    memories = await dao.get_memories(1)
    assert len(memories) == 1
    assert memories[0].content == "test"

    rel = Relationship(agent_id=1, target_id=2, relationship_type="friend", strength=0.9)
    await dao.insert_relationship(rel)
    rels = await dao.get_relationships(1)
    assert len(rels) == 1
    assert rels[0].relationship_type == "friend"

@pytest.mark.asyncio
async def test_add_memory():
    """Test adding a memory to the write queue."""
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
    
    agent = await agent_manager.create_agent(
        name="Test Agent",
        personality=personality,
        style_guide=style_guide
    )
    
    # Add a memory
    content = "This is a test memory"
    await db.add_memory(agent_id=agent.id, content=content)
    
    # Wait for the write queue to flush
    await asyncio.sleep(0.1)
    
    # Retrieve memories
    memories = await db.get_agent_memories(agent_id=agent.id)
    assert len(memories) == 1
    assert memories[0]["content"] == content
    assert memories[0]["agent_id"] == agent.id

@pytest.mark.asyncio
async def test_write_queue_flush():
    """Test that the write queue flushes when it reaches max size."""
    queue = SQLiteWriteQueue(max_size=2, flush_interval=60)
    await queue.start()
    
    try:
        # Add items to the queue
        await queue.enqueue({
            "type": "memory",
            "agent_id": 1,
            "content": "Memory 1",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await queue.enqueue({
            "type": "memory",
            "agent_id": 1,
            "content": "Memory 2",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # The queue should have flushed after the second item
        assert len(queue.queue) == 0
        
    finally:
        await queue.stop()

@pytest.mark.asyncio
async def test_write_queue_periodic_flush():
    """Test that the write queue flushes periodically."""
    queue = SQLiteWriteQueue(max_size=1000, flush_interval=1)
    await queue.start()
    
    try:
        # Add an item to the queue
        await queue.enqueue({
            "type": "memory",
            "agent_id": 1,
            "content": "Memory 1",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Wait for the periodic flush
        await asyncio.sleep(1.1)
        
        # The queue should have been flushed
        assert len(queue.queue) == 0
        
    finally:
        await queue.stop()

@pytest.mark.asyncio
async def test_add_relationship():
    """Test adding a relationship to the write queue."""
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
    
    # Add a relationship
    await db.add_relationship(
        agent_id=agent1.id,
        target_id=agent2.id,
        relationship_type="friend",
        strength=0.8
    )
    
    # Wait for the write queue to flush
    await asyncio.sleep(0.1)
    
    # Retrieve relationships
    relationships = await db.get_agent_relationships(agent_id=agent1.id)
    assert len(relationships) == 1
    assert relationships[0]["target_id"] == agent2.id
    assert relationships[0]["relationship_type"] == "friend"
    assert relationships[0]["strength"] == 0.8

@pytest.mark.asyncio
async def test_concurrent_writes():
    """Test concurrent writes to the write queue."""
    queue = SQLiteWriteQueue(max_size=1000, flush_interval=60)
    await queue.start()
    
    try:
        # Create multiple write tasks
        async def write_task(task_id: int):
            for i in range(10):
                await queue.enqueue({
                    "type": "memory",
                    "agent_id": task_id,
                    "content": f"Memory {i} from task {task_id}",
                    "timestamp": datetime.utcnow().isoformat()
                })
                await asyncio.sleep(0.01)
        
        # Run multiple write tasks concurrently
        tasks = [write_task(i) for i in range(5)]
        await asyncio.gather(*tasks)
        
        # Force a flush
        await queue.flush()
        
        # Verify no items were lost
        assert len(queue.queue) == 0
        
    finally:
        await queue.stop() 