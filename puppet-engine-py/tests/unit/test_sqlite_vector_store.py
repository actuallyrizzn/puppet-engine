import pytest
import numpy as np
import os
from src.memory.sqlite_vector_store import SQLiteVectorStore

@pytest.mark.asyncio
async def test_sqlite_vector_store(tmp_path):
    db_path = tmp_path / "test_sqlite_vector_store.db"
    store = SQLiteVectorStore(str(db_path))

    # Add embedding
    vector = np.random.rand(128).tolist()
    memory_id = "mem1"
    # For test, we need to insert a memory row for the foreign key
    import aiosqlite
    async with aiosqlite.connect(str(db_path)) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS memories (id TEXT PRIMARY KEY, agent_id TEXT)")
        await db.execute("INSERT INTO memories (id, agent_id) VALUES (?, ?)", (memory_id, "agent1"))
        await db.commit()
    success = await store.store_embedding(memory_id, vector)
    assert success

    # Search similar
    results = await store.search_similar(vector, agent_id="agent1", limit=1)
    assert isinstance(results, list)
    assert results and results[0]["memory_id"] == memory_id

    # Delete embedding
    deleted = await store.delete_embedding(memory_id)
    assert deleted
    # Confirm deletion
    results = await store.search_similar(vector, agent_id="agent1", limit=1)
    assert not results

    # Explicitly close the store connection to prevent hangs
    await store.close() 