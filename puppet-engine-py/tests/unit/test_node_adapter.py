import pytest
from unittest.mock import patch, MagicMock
from src.adapters.node_adapter import NodeAdapter

@pytest.fixture
def adapter():
    return NodeAdapter()

def test_send_request(adapter):
    with patch.object(adapter, 'send', return_value={'result': 'ok'}):
        result = adapter.send_request('method', {'param': 1})
        assert result['result'] == 'ok'

def test_send_request_error(adapter):
    with patch.object(adapter, 'send', side_effect=Exception('fail')):
        with pytest.raises(Exception):
            adapter.send_request('method', {'param': 1}) 