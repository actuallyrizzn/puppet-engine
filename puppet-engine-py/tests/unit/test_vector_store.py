import pytest
from unittest.mock import patch, MagicMock
from src.memory.vector_store import VectorStore

@pytest.fixture
def store():
    return VectorStore()

def test_add_vector(store):
    with patch.object(store, 'db', create=True):
        store.db.insert = MagicMock(return_value='id')
        result = store.add_vector({'vector': [1,2,3]})
        assert result == 'id'

def test_get_vector(store):
    with patch.object(store, 'db', create=True):
        store.db.get = MagicMock(return_value={'vector': [1,2,3]})
        result = store.get_vector('id')
        assert result == {'vector': [1,2,3]}

def test_search_vectors(store):
    with patch.object(store, 'db', create=True):
        store.db.search = MagicMock(return_value=[{'vector': [1,2,3]}])
        result = store.search_vectors({'query': 'test'})
        assert isinstance(result, list)

def test_delete_vector(store):
    with patch.object(store, 'db', create=True):
        store.db.delete = MagicMock(return_value=True)
        result = store.delete_vector('id')
        assert result is True 