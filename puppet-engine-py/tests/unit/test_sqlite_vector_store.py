import pytest
from unittest.mock import patch, MagicMock
from src.memory.sqlite_vector_store import SQLiteVectorStore

@pytest.fixture
def store():
    return SQLiteVectorStore(db_path=':memory:')

def test_add_vector(store):
    with patch.object(store, 'add', return_value='id'):
        assert store.add_vector({'vector': [1,2,3]}) == 'id'

def test_get_vector(store):
    with patch.object(store, 'get', return_value={'vector': [1,2,3]}):
        assert store.get_vector('id') == {'vector': [1,2,3]}

def test_search_vectors(store):
    with patch.object(store, 'search', return_value=[{'vector': [1,2,3]}]):
        assert isinstance(store.search_vectors({'query': 'test'}), list)

def test_delete_vector(store):
    with patch.object(store, 'delete', return_value=True):
        assert store.delete_vector('id') is True 