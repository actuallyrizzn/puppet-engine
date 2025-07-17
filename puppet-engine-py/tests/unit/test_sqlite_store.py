import pytest
import asyncio
import os
from src.memory.sqlite_store import SQLiteMemoryStore
from src.core.models import MemoryItem, MemoryType
from datetime import datetime

@pytest.mark.asyncio
async def test_sqlite_memory_store_crud(tmp_path):
    db_path = tmp_path / "test_sqlite_store.db"
    store = SQLiteMemoryStore(str(db_path))

    # Create
    memory = MemoryItem(
        agent_id="agent1",
        type=MemoryType.GENERAL,
        content="test content",
        metadata={"foo": "bar"},
        created_at=datetime.utcnow(),
    )
    memory_id = await store.store_memory(memory)
    assert memory_id is not None

    # Read
    loaded = await store.get_memory(memory_id)
    assert loaded is not None
    assert loaded.content == "test content"

    # Update
    await store.update_memory(memory_id, {"content": "updated"})
    updated = await store.get_memory(memory_id)
    assert updated.content == "updated"

    # Search
    results = await store.search_memories("agent1", "updated")
    assert any(m.content == "updated" for m in results)

    # Get agent memories
    agent_mems = await store.get_agent_memories("agent1")
    assert len(agent_mems) > 0

    # Delete
    deleted = await store.delete_memory(memory_id)
    assert deleted
    assert await store.get_memory(memory_id) is None 