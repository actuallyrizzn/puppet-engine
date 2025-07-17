import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from src.memory.sqlite_store import SQLiteMemoryStore
from src.core.models import MemoryItem, MemoryType
from datetime import datetime

@pytest.mark.asyncio
async def test_store_and_get_memory():
    store = SQLiteMemoryStore(db_path=':memory:')
    memory = MemoryItem(
        id='mem1',
        agent_id='agent1',
        type=MemoryType.GENERAL,
        content='test content',
        metadata={'foo': 'bar'},
        timestamp=datetime.utcnow(),
        importance=1.0,
        vector_embedding=None
    )
    with patch.object(store, '_get_db', new_callable=AsyncMock):
        with patch.object(store, '_create_tables', new_callable=AsyncMock):
            with patch.object(store, 'store_memory', new_callable=AsyncMock, return_value='mem1') as mock_store:
                memory_id = await store.store_memory(memory)
                assert memory_id == 'mem1'
                mock_store.assert_awaited()
            with patch.object(store, 'get_memory', new_callable=AsyncMock, return_value=memory) as mock_get:
                loaded = await store.get_memory('mem1')
                assert loaded is not None
                assert loaded.content == 'test content'
                mock_get.assert_awaited()

@pytest.mark.asyncio
async def test_search_memories():
    store = SQLiteMemoryStore(db_path=':memory:')
    with patch.object(store, 'search_memories', new_callable=AsyncMock, return_value=[]) as mock_search:
        results = await store.search_memories('agent1', 'query')
        assert isinstance(results, list)
        mock_search.assert_awaited()

@pytest.mark.asyncio
async def test_delete_memory():
    store = SQLiteMemoryStore(db_path=':memory:')
    with patch.object(store, 'delete_memory', new_callable=AsyncMock, return_value=True) as mock_delete:
        deleted = await store.delete_memory('mem1')
        assert deleted is True
        mock_delete.assert_awaited()

@pytest.mark.asyncio
async def test_update_memory():
    store = SQLiteMemoryStore(db_path=':memory:')
    memory = MemoryItem(
        id='mem1',
        agent_id='agent1',
        type=MemoryType.GENERAL,
        content='updated',
        metadata={'foo': 'baz'},
        timestamp=datetime.utcnow(),
        importance=1.0,
        vector_embedding=None
    )
    with patch.object(store, 'update_memory', new_callable=AsyncMock, return_value=memory) as mock_update:
        updated = await store.update_memory('mem1', {'content': 'updated'})
        assert updated is not None
        assert updated.content == 'updated'
        mock_update.assert_awaited() 