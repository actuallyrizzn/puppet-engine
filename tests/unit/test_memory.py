import pytest
from src.memory.base import MemoryStore
from src.core.models import MemoryItem, MemoryType
from unittest.mock import AsyncMock, patch, MagicMock

class DummyMemoryStore(MemoryStore):
    async def store_memory(self, memory): return "id"
    async def get_memory(self, memory_id): return None
    async def search_memories(self, agent_id, query, limit=10): return []
    async def get_agent_memories(self, agent_id, memory_type=None, limit=50): return []
    async def delete_memory(self, memory_id): return True
    async def update_memory(self, memory_id, updates): return None

@pytest.mark.asyncio
async def test_memory_store_abstract():
    store = DummyMemoryStore()
    result = await store.store_memory(MemoryItem(agent_id="a", type=MemoryType.CORE, content="c"))
    assert result == "id"

@pytest.mark.asyncio
async def test_memory_store_get_memory():
    store = DummyMemoryStore()
    result = await store.get_memory("test_id")
    assert result is None

@pytest.mark.asyncio
async def test_memory_store_search_memories():
    store = DummyMemoryStore()
    result = await store.search_memories("agent1", "test query")
    assert result == []

@pytest.mark.asyncio
async def test_memory_store_get_agent_memories():
    store = DummyMemoryStore()
    result = await store.get_agent_memories("agent1")
    assert result == []

@pytest.mark.asyncio
async def test_memory_store_delete_memory():
    store = DummyMemoryStore()
    result = await store.delete_memory("test_id")
    assert result is True

@pytest.mark.asyncio
async def test_memory_store_update_memory():
    store = DummyMemoryStore()
    result = await store.update_memory("test_id", {"content": "updated"})
    assert result is None 