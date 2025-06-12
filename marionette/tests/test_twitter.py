import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from ..twitter.client import TwitterClient
from ..types import Agent, Event
from ..events.handlers import EVENT_TYPES

@pytest.fixture
def mock_tweepy():
    """Mock Tweepy API for testing."""
    with patch("tweepy.API") as mock:
        mock_api = MagicMock()
        mock.return_value = mock_api
        
        # Mock tweet response
        mock_tweet = MagicMock()
        mock_tweet.id = "123456789"
        mock_tweet.text = "Test tweet"
        mock_tweet.created_at = datetime.utcnow()
        mock_api.update_status.return_value = mock_tweet
        
        # Mock get_status response
        mock_original = MagicMock()
        mock_original.id = "987654321"
        mock_original.user.screen_name = "test_user"
        mock_api.get_status.return_value = mock_original
        
        yield mock_api

@pytest.fixture
def mock_event_router():
    """Mock event router for testing."""
    with patch("marionette.events.router.event_router") as mock:
        mock.dispatch_event = AsyncMock()
        yield mock

@pytest.fixture
def test_credentials():
    """Test Twitter credentials."""
    return [
        {
            "consumer_key": "test_key_1",
            "consumer_secret": "test_secret_1",
            "access_token": "test_token_1",
            "access_token_secret": "test_secret_1"
        },
        {
            "consumer_key": "test_key_2",
            "consumer_secret": "test_secret_2",
            "access_token": "test_token_2",
            "access_token_secret": "test_secret_2"
        }
    ]

@pytest.fixture
def test_agent():
    """Create a test agent."""
    return Agent(
        id="test-agent-1",
        name="Test Agent",
        personality={
            "name": "Test Personality",
            "description": "A test personality",
            "traits": ["friendly", "curious"]
        },
        style_guide={
            "tone": "casual",
            "language": "english",
            "quirks": ["uses emojis", "talks in third person"]
        }
    )

@pytest.fixture
def mock_twitter_credentials():
    return [{
        "consumer_key": "test_consumer_key",
        "consumer_secret": "test_consumer_secret",
        "access_token": "test_access_token",
        "access_token_secret": "test_access_token_secret"
    }]

@pytest.fixture
def mock_bearer_token():
    return "test_bearer_token"

@pytest.fixture
def mock_agent():
    return Agent(
        id="test-agent",
        name="Test Agent",
        description="A test agent",
        personality="Friendly and helpful",
        mood="happy",
        created_at=datetime.utcnow().isoformat()
    )

@pytest.fixture
def twitter_client(mock_twitter_credentials, mock_bearer_token):
    with patch("tweepy.Client") as mock_client:
        # Mock the default client
        mock_default_client = MagicMock()
        mock_default_client.get_me.return_value = MagicMock(data=MagicMock(username="test_user"))
        mock_default_client.create_tweet.return_value = MagicMock(data={"id": "123456"})
        
        # Mock the bearer client
        mock_bearer_client = MagicMock()
        mock_bearer_client.bearer_token = mock_bearer_token
        
        # Configure the mock to return different clients
        mock_client.side_effect = [mock_default_client, mock_bearer_client]
        
        client = TwitterClient(mock_twitter_credentials, mock_bearer_token)
        client.default_client = mock_default_client
        client.bearer_client = mock_bearer_client
        yield client

@pytest.mark.asyncio
async def test_post_tweet(twitter_client, test_agent, mock_tweepy, mock_event_router):
    """Test posting a tweet."""
    result = await twitter_client.post_tweet(test_agent, "Test tweet content")
    
    assert result["id"] == "123456789"
    assert result["content"] == "Test tweet"
    assert "created_at" in result
    
    # Check event dispatch
    mock_event_router.dispatch_event.assert_called_once()
    event = mock_event_router.dispatch_event.call_args[0][0]
    assert event.type == EVENT_TYPES["TWEET_POSTED"]
    assert event.agent_id == test_agent.id
    assert event.data["tweet_id"] == "123456789"
    assert event.data["content"] == "Test tweet content"

@pytest.mark.asyncio
async def test_reply_to_tweet(twitter_client, test_agent, mock_tweepy, mock_event_router):
    """Test replying to a tweet."""
    result = await twitter_client.reply_to_tweet(
        test_agent,
        "987654321",
        "Test reply content"
    )
    
    assert result["id"] == "123456789"
    assert result["content"] == "Test tweet"
    assert result["in_reply_to"]["id"] == "987654321"
    assert result["in_reply_to"]["user"] == "test_user"
    
    # Check event dispatch
    mock_event_router.dispatch_event.assert_called_once()
    event = mock_event_router.dispatch_event.call_args[0][0]
    assert event.type == EVENT_TYPES["TWEET_REPLIED"]
    assert event.agent_id == test_agent.id
    assert event.data["tweet_id"] == "123456789"
    assert event.data["original_tweet_id"] == "987654321"
    assert event.data["content"] == "Test reply content"

@pytest.mark.asyncio
async def test_rate_limit_handling(twitter_client, test_agent, mock_tweepy):
    """Test rate limit handling and credential rotation."""
    # Exhaust rate limit
    for _ in range(200):
        await twitter_client._check_rate_limit("tweets")
    
    # Next call should rotate credentials
    assert twitter_client.current_cred_index == 0
    await twitter_client._check_rate_limit("tweets")
    assert twitter_client.current_cred_index == 1

@pytest.mark.asyncio
async def test_rate_limit_reset(twitter_client):
    """Test rate limit reset after time period."""
    # Set reset time to past
    twitter_client._rate_limits["tweets"]["reset_time"] = datetime.utcnow() - timedelta(minutes=1)
    
    # Check rate limit should reset
    assert await twitter_client._check_rate_limit("tweets")
    assert twitter_client._rate_limits["tweets"]["remaining"] == 199
    assert twitter_client._rate_limits["tweets"]["reset_time"] > datetime.utcnow()

def test_get_rate_limits(twitter_client):
    """Test getting rate limit status."""
    limits = twitter_client.get_rate_limits()
    
    assert "tweets" in limits
    assert "replies" in limits
    assert "remaining" in limits["tweets"]
    assert "reset_time" in limits["tweets"]
    assert "remaining" in limits["replies"]
    assert "reset_time" in limits["replies"]

@pytest.mark.asyncio
async def test_error_handling(twitter_client, test_agent, mock_tweepy):
    """Test error handling and retry logic."""
    # Mock rate limit error
    mock_tweepy.update_status.side_effect = Exception("Rate limit exceeded")
    
    with pytest.raises(Exception) as exc_info:
        await twitter_client.post_tweet(test_agent, "Test tweet")
    
    assert "Rate limit exceeded" in str(exc_info.value)
    assert twitter_client.current_cred_index == 1  # Should have rotated credentials 

def test_register_agent_client(twitter_client, mock_agent):
    """Test registering a Twitter client for an agent."""
    agent_credentials = {
        "consumer_key": "agent_consumer_key",
        "consumer_secret": "agent_consumer_secret",
        "access_token": "agent_access_token",
        "access_token_secret": "agent_access_token_secret"
    }
    
    client = twitter_client.register_agent_client(mock_agent.id, agent_credentials)
    assert client is not None
    assert mock_agent.id in twitter_client.clients

def test_get_client_for_agent(twitter_client, mock_agent):
    """Test getting the appropriate client for an agent."""
    # Test with registered agent
    agent_credentials = {
        "consumer_key": "agent_consumer_key",
        "consumer_secret": "agent_consumer_secret",
        "access_token": "agent_access_token",
        "access_token_secret": "agent_access_token_secret"
    }
    twitter_client.register_agent_client(mock_agent.id, agent_credentials)
    client = twitter_client.get_client_for_agent(mock_agent.id)
    assert client is not None
    
    # Test with unregistered agent (should use default client)
    other_agent = Agent(
        id="other-agent",
        name="Other Agent",
        description="Another test agent",
        personality="Friendly and helpful",
        mood="happy",
        created_at=datetime.utcnow().isoformat()
    )
    client = twitter_client.get_client_for_agent(other_agent.id)
    assert client == twitter_client.default_client

@pytest.mark.asyncio
async def test_post_tweet_with_options(twitter_client, mock_agent):
    """Test posting a tweet with various options."""
    # Test reply
    content = "@user Hello!"
    options = {"reply_to_tweet_id": "789012"}
    result = await twitter_client.post_tweet(mock_agent, content, options)
    assert "Hello!" in result["content"]
    
    # Test quote tweet
    content = "Check this out!"
    options = {"quote_tweet_id": "789012"}
    result = await twitter_client.post_tweet(mock_agent, content, options)
    assert "https://twitter.com/i/status/789012" in result["content"]
    
    # Test media
    content = "Look at this image!"
    options = {"media_ids": ["media1", "media2"]}
    result = await twitter_client.post_tweet(mock_agent, content, options)
    assert result["content"] == content

@pytest.mark.asyncio
async def test_start_mention_stream(twitter_client, mock_agent):
    """Test starting a mention stream."""
    async def mock_callback(tweet):
        pass
    
    result = await twitter_client.start_mention_stream(mock_agent, mock_callback)
    assert result["agent_id"] == mock_agent.id
    assert result["username"] == "test_user"
    assert "started_at" in result
    assert mock_agent.id in twitter_client.active_streams

def test_stop_mention_stream(twitter_client, mock_agent):
    """Test stopping a mention stream."""
    # Start a stream
    mock_stream = MagicMock()
    twitter_client.active_streams[mock_agent.id] = mock_stream
    
    # Stop the stream
    twitter_client.stop_mention_stream(mock_agent.id)
    mock_stream.disconnect.assert_called_once()
    assert mock_agent.id not in twitter_client.active_streams

@pytest.mark.asyncio
async def test_get_user_timeline(twitter_client, mock_agent):
    """Test getting a user's timeline."""
    # Mock timeline response
    mock_tweet = MagicMock()
    mock_tweet.id = "123456"
    mock_tweet.text = "Test tweet"
    mock_tweet.created_at = datetime.utcnow()
    mock_tweet.public_metrics = {"retweets": 0, "likes": 0}
    
    twitter_client.default_client.get_users_tweets.return_value = MagicMock(data=[mock_tweet])
    
    result = await twitter_client.get_user_timeline(mock_agent, "user123")
    assert len(result) == 1
    assert result[0]["id"] == "123456"
    assert result[0]["text"] == "Test tweet"
    assert "created_at" in result[0]
    assert "metrics" in result[0]

@pytest.mark.asyncio
async def test_error_handling_in_various_operations(twitter_client, mock_agent):
    """Test error handling in various operations."""
    # Test post_tweet error
    twitter_client.default_client.create_tweet.side_effect = Exception("API Error")
    with pytest.raises(Exception) as exc_info:
        await twitter_client.post_tweet(mock_agent, "Test tweet")
    assert "API Error" in str(exc_info.value)
    
    # Test get_user_timeline error
    twitter_client.default_client.get_users_tweets.side_effect = Exception("API Error")
    with pytest.raises(Exception) as exc_info:
        await twitter_client.get_user_timeline(mock_agent, "user123")
    assert "API Error" in str(exc_info.value)
    
    # Test start_mention_stream error
    twitter_client.bearer_client = None
    with pytest.raises(Exception) as exc_info:
        await twitter_client.start_mention_stream(mock_agent, lambda x: None)
    assert "Bearer token required" in str(exc_info.value) 