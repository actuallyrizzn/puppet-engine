import pytest
from src.twitter.client import TwitterXClient
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch("src.twitter.client.httpx.AsyncClient")
async def test_post_tweet(mock_client):
    mock_instance = mock_client.return_value
    mock_response = AsyncMock()
    mock_response.status_code = 200
    # Mock json() to return the data directly, not a coroutine
    mock_response.json.return_value = {"id": "123"}
    mock_response.raise_for_status = AsyncMock()
    mock_response.headers = {}
    mock_instance.post = AsyncMock(return_value=mock_response)
    
    client = TwitterXClient({"bearer_token": "token"})
    # The post_tweet method should return the JSON response directly
    resp = await client.post_tweet("hello")
    # Check that the method was called correctly
    mock_instance.post.assert_called_once()
    # The actual response should be the JSON data
    assert resp == {"id": "123"} 