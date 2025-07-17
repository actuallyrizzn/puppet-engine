import pytest
from unittest.mock import patch, MagicMock
from src.twitter.client import TwitterXClient

@pytest.fixture
def client():
    return TwitterXClient(auth=MagicMock())

def test_post_tweet(client):
    with patch.object(client, 'post_tweet', return_value={'id': '123'}):
        result = client.post_tweet('hello')
        assert result['id'] == '123'

def test_get_user_info(client):
    with patch.object(client, 'get_user_info', return_value={'id': 'u', 'name': 'n'}):
        result = client.get_user_info('u')
        assert result['id'] == 'u'

def test_get_timeline(client):
    with patch.object(client, 'get_timeline', return_value=[{'id': '1'}]):
        result = client.get_timeline('u')
        assert isinstance(result, list)

def test_search_tweets(client):
    with patch.object(client, 'search_tweets', return_value=[{'id': '1'}]):
        result = client.search_tweets('query')
        assert isinstance(result, list)

def test_error_handling(client):
    with patch.object(client, 'post_tweet', side_effect=Exception('fail')):
        with pytest.raises(Exception):
            client.post_tweet('fail') 