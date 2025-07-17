import pytest
from unittest.mock import patch, MagicMock
from src.memory.mongo_store import MongoMemoryStore

@pytest.fixture
def store():
    with patch('src.memory.mongo_store.MongoClient'):
        return MongoMemoryStore()

def test_init(store):
    assert hasattr(store, 'client')
    assert hasattr(store, 'db')
    assert hasattr(store, 'collection')

def test_add_memory(store):
    with patch.object(store.collection, 'insert_one', return_value=MagicMock(inserted_id='id')) as mock_insert:
        result = store.add_memory({'foo': 'bar'})
        assert result == 'id'
        mock_insert.assert_called()

def test_get_memory(store):
    with patch.object(store.collection, 'find_one', return_value={'foo': 'bar'}):
        result = store.get_memory('id')
        assert result == {'foo': 'bar'}

def test_search_memories(store):
    with patch.object(store.collection, 'find', return_value=[{'foo': 'bar'}]):
        result = store.search_memories({'query': 'test'})
        assert isinstance(result, list)

def test_delete_memory(store):
    with patch.object(store.collection, 'delete_one', return_value=MagicMock(deleted_count=1)):
        result = store.delete_memory('id')
        assert result is True

def test_update_memory(store):
    with patch.object(store.collection, 'update_one', return_value=MagicMock(matched_count=1)):
        result = store.update_memory('id', {'foo': 'baz'})
        assert result is True 