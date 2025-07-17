import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.memory.sqlite_vector_store import SQLiteVectorStore

@pytest.fixture
def store():
    return SQLiteVectorStore(db_path=':memory:')

@pytest.mark.asyncio
async def test_add_vector(store):
    with patch.object(store, 'store_embedding', new_callable=AsyncMock, return_value=True):
        result = await store.store_embedding('mem1', [1,2,3])
        assert result is True

@pytest.mark.asyncio
async def test_get_vector(store):
    with patch.object(store, 'search_similar', new_callable=AsyncMock, return_value=[{'memory_id': 'id', 'similarity': 0.8}]):
        result = await store.search_similar([1,2,3])
        assert len(result) == 1
        assert result[0]['memory_id'] == 'id'

@pytest.mark.asyncio
async def test_search_vectors(store):
    with patch.object(store, 'search_similar', new_callable=AsyncMock, return_value=[{'memory_id': 'id', 'similarity': 0.8}]):
        result = await store.search_similar([1,2,3])
        assert isinstance(result, list)
        assert len(result) == 1

@pytest.mark.asyncio
async def test_delete_vector(store):
    with patch.object(store, 'delete_embedding', new_callable=AsyncMock, return_value=True):
        result = await store.delete_embedding('id')
        assert result is True 