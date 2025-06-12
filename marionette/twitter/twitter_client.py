import tweepy
import os
from typing import Optional

class TwitterClient:
    def __init__(self, api_key=None, api_secret=None, access_token=None, access_token_secret=None):
        self.api_key = api_key or os.getenv("TWITTER_API_KEY")
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET")
        self.access_token = access_token or os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = access_token_secret or os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        self.client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret
        )

    async def post_tweet(self, text: str) -> Optional[int]:
        try:
            tweet = await self.client.create_tweet(text=text)
            return tweet.data["id"]
        except tweepy.TooManyRequests:
            # Rate limit hit
            return None

    async def reply(self, text: str, in_reply_to_tweet_id: int) -> Optional[int]:
        try:
            tweet = await self.client.create_tweet(text=text, in_reply_to_tweet_id=in_reply_to_tweet_id)
            return tweet.data["id"]
        except tweepy.TooManyRequests:
            return None

    def rotate_credentials(self):
        # Stub for credential rotation
        pass 