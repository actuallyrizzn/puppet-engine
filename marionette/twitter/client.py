import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
import re
import tweepy
from tweepy import Stream, StreamRule
from ..types import Agent
from ..events.router import event_router
from ..events.handlers import EVENT_TYPES

class TwitterClient:
    """Twitter client with streaming support and per-agent clients."""
    
    def __init__(self, credentials: List[Dict[str, str]], bearer_token: Optional[str] = None):
        self.clients: Dict[str, tweepy.Client] = {}
        self.default_client = None
        self.bearer_client = None
        self.active_streams = {}
        self._lock = asyncio.Lock()
        
        # Initialize default client if credentials provided
        if credentials:
            self.default_client = self._create_client(credentials[0])
            
            # Create bearer token client for elevated access
            if bearer_token:
                self.bearer_client = tweepy.Client(
                    bearer_token=bearer_token,
                    wait_on_rate_limit=True
                )
    
    def _create_client(self, credentials: Dict[str, str]) -> tweepy.Client:
        """Create a new Twitter client with credentials."""
        return tweepy.Client(
            consumer_key=credentials["consumer_key"],
            consumer_secret=credentials["consumer_secret"],
            access_token=credentials["access_token"],
            access_token_secret=credentials["access_token_secret"],
            wait_on_rate_limit=True
        )
    
    def register_agent_client(self, agent_id: str, credentials: Dict[str, str]) -> Optional[tweepy.Client]:
        """Register a Twitter client for an agent."""
        if not all(k in credentials for k in ["consumer_key", "consumer_secret", "access_token", "access_token_secret"]):
            print(f"Incomplete Twitter credentials for agent {agent_id}. Using default client if available.")
            return None
        
        try:
            self.clients[agent_id] = self._create_client(credentials)
            print(f"Successfully registered Twitter client for agent {agent_id}")
            return self.clients[agent_id]
        except Exception as e:
            print(f"Error registering Twitter client for agent {agent_id}: {e}")
            raise
    
    def get_client_for_agent(self, agent_id: str) -> tweepy.Client:
        """Get the appropriate client for an agent."""
        client = self.clients.get(agent_id, self.default_client)
        if not client:
            raise Exception(f"No Twitter client available for agent {agent_id}")
        return client
    
    async def post_tweet(
        self,
        agent: Agent,
        content: str,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Post a tweet for an agent."""
        options = options or {}
        client = self.get_client_for_agent(agent.id)
        
        try:
            # Test authentication
            me = client.get_me()
            print(f"Successfully authenticated as: {me.data.username}")
            
            tweet_params = {}
            
            # Handle reply
            if options.get("reply_to_tweet_id"):
                tweet_params["in_reply_to_tweet_id"] = options["reply_to_tweet_id"]
                # Clean up @mentions as Twitter handles threading
                content = re.sub(r'^@\w+\s+', '', content)  # Remove leading @mention
                content = re.sub(r'@\w+', '', content)  # Remove other @mentions
                content = content.strip()
            
            # Handle quote tweet
            if options.get("quote_tweet_id"):
                content = f"{content} https://twitter.com/i/status/{options['quote_tweet_id']}"
            
            # Handle media
            if options.get("media_ids"):
                tweet_params["media_ids"] = options["media_ids"]
            
            # Special case for Coby agent
            if agent.id == "coby-agent":
                content = content.lower()
            
            # Post tweet
            tweet = client.create_tweet(text=content, **tweet_params)
            
            # Dispatch tweet event
            await event_router.dispatch_event(Event(
                type=EVENT_TYPES["TWEET_POSTED"],
                agent_id=agent.id,
                data={
                    "tweet_id": tweet.data["id"],
                    "content": content,
                    "timestamp": datetime.utcnow().isoformat()
                }
            ))
            
            return {
                "id": tweet.data["id"],
                "content": content,
                "created_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            # Dispatch error event
            await event_router.dispatch_event(Event(
                type=EVENT_TYPES["ERROR_OCCURRED"],
                agent_id=agent.id,
                data={
                    "error": str(e),
                    "operation": "post_tweet"
                }
            ))
            raise
    
    async def start_mention_stream(
        self,
        agent: Agent,
        on_mention: Callable,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Start streaming mentions for an agent."""
        options = options or {}
        client = self.get_client_for_agent(agent.id)
        
        if not self.bearer_client:
            raise Exception("Bearer token required for streaming API access")
        
        try:
            # Configure stream parameters
            stream_params = {
                "tweet_fields": ["created_at", "author_id", "conversation_id", "referenced_tweets"],
                "expansions": ["author_id", "referenced_tweets.id", "in_reply_to_user_id"],
                "user_fields": ["name", "username"]
            }
            
            # Create stream listener
            class MentionListener(tweepy.StreamingClient):
                def __init__(self, bearer_token, callback):
                    super().__init__(bearer_token)
                    self.callback = callback
                
                def on_tweet(self, tweet):
                    asyncio.create_task(self.callback(tweet))
            
            # Start stream
            listener = MentionListener(self.bearer_client.bearer_token, on_mention)
            listener.add_rules([StreamRule(f"@{me.data.username}")])
            listener.filter(**stream_params)
            
            # Store stream reference
            self.active_streams[agent.id] = listener
            
            return {
                "agent_id": agent.id,
                "username": me.data.username,
                "started_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            # Dispatch error event
            await event_router.dispatch_event(Event(
                type=EVENT_TYPES["ERROR_OCCURRED"],
                agent_id=agent.id,
                data={
                    "error": str(e),
                    "operation": "start_mention_stream"
                }
            ))
            raise
    
    def stop_mention_stream(self, agent_id: str) -> None:
        """Stop streaming mentions for an agent."""
        if agent_id in self.active_streams:
            self.active_streams[agent_id].disconnect()
            del self.active_streams[agent_id]
    
    async def get_user_timeline(
        self,
        agent: Agent,
        user_id: str,
        options: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Get recent tweets from a user timeline."""
        options = options or {}
        client = self.get_client_for_agent(agent.id)
        
        try:
            tweets = client.get_users_tweets(
                user_id,
                max_results=options.get("max_results", 10),
                tweet_fields=["created_at", "public_metrics"]
            )
            
            return [{
                "id": tweet.id,
                "text": tweet.text,
                "created_at": tweet.created_at.isoformat(),
                "metrics": tweet.public_metrics
            } for tweet in tweets.data or []]
        except Exception as e:
            # Dispatch error event
            await event_router.dispatch_event(Event(
                type=EVENT_TYPES["ERROR_OCCURRED"],
                agent_id=agent.id,
                data={
                    "error": str(e),
                    "operation": "get_user_timeline"
                }
            ))
            raise 