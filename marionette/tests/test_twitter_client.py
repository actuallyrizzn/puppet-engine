import pytest
from marionette.twitter.twitter_client import TwitterClient
import tweepy

class DummyTweet:
    def __init__(self, id):
        self.data = {"id": id}

@pytest.mark.asyncio
async def test_post_tweet(monkeypatch):
    async def fake_create_tweet(self, text=None, in_reply_to_tweet_id=None):
        return DummyTweet(123)
    monkeypatch.setattr(tweepy.Client, "create_tweet", fake_create_tweet)
    client = TwitterClient(api_key="a", api_secret="b", access_token="c", access_token_secret="d")
    tweet_id = await client.post_tweet("hello")
    assert tweet_id == 123

@pytest.mark.asyncio
async def test_reply(monkeypatch):
    async def fake_create_tweet(self, text=None, in_reply_to_tweet_id=None):
        return DummyTweet(456)
    monkeypatch.setattr(tweepy.Client, "create_tweet", fake_create_tweet)
    client = TwitterClient(api_key="a", api_secret="b", access_token="c", access_token_secret="d")
    tweet_id = await client.reply("hi", 789)
    assert tweet_id == 456

def test_rotate_credentials():
    client = TwitterClient(api_key="a", api_secret="b", access_token="c", access_token_secret="d")
    client.rotate_credentials()  # Should not raise 