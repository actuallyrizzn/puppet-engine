import pytest
from src.adapters.node_adapter import NodeAdapter
from src.core.settings import Settings
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch("src.adapters.node_adapter.httpx.AsyncClient")
async def test_forward_request(mock_client):
    mock_instance = mock_client.return_value
    mock_response = AsyncMock()
    # Mock json() to return the data directly, not a coroutine
    mock_response.json.return_value = {"ok": True}
    mock_response.raise_for_status = AsyncMock()
    mock_instance.request = AsyncMock(return_value=mock_response)
    
    adapter = NodeAdapter(Settings())
    # The forward_request method should return the JSON response directly
    resp = await adapter.forward_request("GET", "/test")
    # Check that the method was called correctly
    mock_instance.request.assert_called_once()
    # The actual response should be the JSON data
    assert resp == {"ok": True} 