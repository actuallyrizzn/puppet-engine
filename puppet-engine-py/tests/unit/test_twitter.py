import pytest
from src.twitter.client import TwitterXClient
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

@pytest.mark.asyncio
@patch("src.twitter.client.httpx.AsyncClient")
async def test_post_tweet(mock_client):
    mock_instance = mock_client.return_value
    mock_response = MagicMock()  # Use MagicMock instead of AsyncMock for response
    mock_response.status_code = 200
    # Mock json() as a regular method, not async
    mock_response.json.return_value = {"id": "123"}
    mock_response.raise_for_status = MagicMock()
    mock_response.headers = {}
    mock_instance.post = AsyncMock(return_value=mock_response)
    
    client = TwitterXClient({"bearer_token": "token"})
    # The post_tweet method should return the JSON response directly
    resp = await client.post_tweet("hello")
    # Check that the method was called correctly
    mock_instance.post.assert_called_once()
    # The actual response should be the JSON data
    assert resp == {"id": "123"}

@pytest.mark.asyncio
@patch("src.twitter.client.httpx.AsyncClient")
async def test_post_tweet_with_reply(mock_client):
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "456"}
    mock_response.raise_for_status = MagicMock()
    mock_response.headers = {}
    mock_instance.post = AsyncMock(return_value=mock_response)
    
    client = TwitterXClient({"bearer_token": "token"})
    resp = await client.post_tweet("reply", reply_to="123")
    
    # Check that reply data was included
    call_args = mock_instance.post.call_args
    assert "reply" in call_args[1]["json"]
    assert call_args[1]["json"]["reply"]["in_reply_to_tweet_id"] == "123"

@pytest.mark.asyncio
@patch("src.twitter.client.httpx.AsyncClient")
async def test_post_tweet_rate_limit(mock_client):
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {"x-rate-limit-reset": str(int(1234567890))}
    mock_response.json.return_value = {"id": "123"}
    mock_response.raise_for_status = MagicMock()
    mock_instance.post = AsyncMock(return_value=mock_response)
    
    client = TwitterXClient({"bearer_token": "token"})
    resp = await client.post_tweet("hello")
    
    # Should have been called twice (once for rate limit, once for retry)
    assert mock_instance.post.call_count == 2

@pytest.mark.asyncio
@patch("src.twitter.client.httpx.AsyncClient")
async def test_get_user_info(mock_client):
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "123", "username": "testuser"}
    mock_response.raise_for_status = MagicMock()
    mock_instance.get = AsyncMock(return_value=mock_response)
    
    client = TwitterXClient({"bearer_token": "token"})
    resp = await client.get_user_info("testuser")
    
    assert resp["username"] == "testuser"
    mock_instance.get.assert_called_once()

@pytest.mark.asyncio
@patch("src.twitter.client.httpx.AsyncClient")
async def test_get_timeline(mock_client):
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [{"id": "123", "text": "test"}]}
    mock_response.raise_for_status = MagicMock()
    mock_instance.get = AsyncMock(return_value=mock_response)
    
    client = TwitterXClient({"bearer_token": "token"})
    resp = await client.get_timeline("123", max_results=5)
    
    assert "data" in resp
    mock_instance.get.assert_called_once()

@pytest.mark.asyncio
@patch("src.twitter.client.httpx.AsyncClient")
async def test_search_tweets(mock_client):
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [{"id": "123", "text": "search result"}]}
    mock_response.raise_for_status = MagicMock()
    mock_instance.get = AsyncMock(return_value=mock_response)
    
    client = TwitterXClient({"bearer_token": "token"})
    resp = await client.search_tweets("python", max_results=10)
    
    assert "data" in resp
    mock_instance.get.assert_called_once()

@pytest.mark.asyncio
@patch("src.twitter.client.httpx.AsyncClient")
async def test_twitter_error_handling(mock_client):
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "400 Bad Request", request=None, response=mock_response
    )
    mock_instance.post = AsyncMock(return_value=mock_response)
    
    client = TwitterXClient({"bearer_token": "token"})
    
    with pytest.raises(Exception) as exc_info:
        await client.post_tweet("hello")
    
    assert "400" in str(exc_info.value)
    assert "Bad Request" in str(exc_info.value)

@pytest.mark.asyncio
@patch("src.twitter.client.httpx.AsyncClient")
async def test_twitter_client_close(mock_client):
    mock_instance = mock_client.return_value
    mock_instance.aclose = AsyncMock()
    
    client = TwitterXClient({"bearer_token": "token"})
    await client.close()
    
    mock_instance.aclose.assert_called_once()

def test_twitter_client_init():
    credentials = {
        "api_key": "test_key",
        "api_secret": "test_secret", 
        "bearer_token": "test_bearer"
    }
    
    with patch("src.twitter.client.httpx.AsyncClient"):
        client = TwitterXClient(credentials)
        
        assert client.api_key == "test_key"
        assert client.api_secret == "test_secret"
        assert client.bearer_token == "test_bearer"
        assert client.base_url == "https://api.twitter.com/2" 