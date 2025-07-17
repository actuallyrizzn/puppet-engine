import pytest
from unittest.mock import patch, MagicMock
from src.memory.sqlite_store import SQLiteMemoryStore

@pytest.fixture
def store():
    return SQLiteMemoryStore(db_path=':memory:')

def test_add_memory(store):
    with patch.object(store, 'add', return_value='id'):
        assert store.add_memory({'foo': 'bar'}) == 'id'

def test_get_memory(store):
    with patch.object(store, 'get', return_value={'foo': 'bar'}):
        assert store.get_memory('id') == {'foo': 'bar'}

def test_search_memories(store):
    with patch.object(store, 'search', return_value=[{'foo': 'bar'}]):
        assert isinstance(store.search_memories({'query': 'test'}), list)

def test_delete_memory(store):
    with patch.object(store, 'delete', return_value=True):
        assert store.delete_memory('id') is True

def test_update_memory(store):
    with patch.object(store, 'update', return_value=True):
        assert store.update_memory('id', {'foo': 'baz'}) is True 