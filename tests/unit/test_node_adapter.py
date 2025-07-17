import pytest
from unittest.mock import patch, MagicMock
from src.adapters.node_adapter import NodeAdapter
from src.core.settings import Settings

@pytest.fixture
def adapter():
    settings = Settings()
    return NodeAdapter(settings=settings)

@pytest.mark.asyncio
async def test_forward_request(adapter):
    with patch.object(adapter, 'forward_request', return_value={'result': 'ok'}):
        result = await adapter.forward_request('GET', '/test', {'param': 1})
        assert result['result'] == 'ok'

@pytest.mark.asyncio
async def test_forward_request_error(adapter):
    with patch.object(adapter, 'forward_request', side_effect=Exception('fail')):
        with pytest.raises(Exception):
            await adapter.forward_request('GET', '/test', {'param': 1}) 