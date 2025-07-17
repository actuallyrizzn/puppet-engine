import httpx
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
from ..core.models import Tweet

class TwitterXClient:
    def __init__(self, credentials: Dict[str, str]):
        self.api_key = credentials.get('api_key')
        self.api_secret = credentials.get('api_secret')
        self.access_token = credentials.get('access_token')
        self.bearer_token = credentials.get('bearer_token')
        
        self.client = httpx.AsyncClient(timeout=30.0)
        self.rate_limit_remaining = 300
        self.rate_limit_reset = None
        self.base_url = "https://api.twitter.com/2"
    
    async def post_tweet(self, text: str, reply_to: Optional[str] = None) -> Dict[str, Any]:
        """Post a tweet using Twitter API v2"""
        url = f"{self.base_url}/tweets"
        data = {"text": text}
        if reply_to:
            data["reply"] = {"in_reply_to_tweet_id": reply_to}
        
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.client.post(url, json=data, headers=headers)
            
            # Handle rate limiting
            if response.status_code == 429:
                await self._handle_rate_limit(response)
                # Retry after rate limit
                response = await self.client.post(url, json=data, headers=headers)
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise Exception(f"Twitter API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Twitter API error: {e}")
    
    async def _handle_rate_limit(self, response: httpx.Response) -> None:
        """Handle rate limiting by waiting for reset time"""
        if response.status_code == 429:
            reset_time = response.headers.get('x-rate-limit-reset')
            if reset_time:
                wait_time = int(reset_time) - int(datetime.now().timestamp())
                if wait_time > 0:
                    await asyncio.sleep(wait_time + 1)
    
    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """Get user information by username"""
        url = f"{self.base_url}/users/by/username/{username}"
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        
        try:
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"Twitter API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Twitter API error: {e}")
    
    async def get_timeline(self, user_id: str, max_results: int = 10) -> Dict[str, Any]:
        """Get user timeline"""
        url = f"{self.base_url}/users/{user_id}/tweets"
        params = {"max_results": max_results}
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        
        try:
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"Twitter API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Twitter API error: {e}")
    
    async def search_tweets(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search tweets"""
        url = f"{self.base_url}/tweets/search/recent"
        params = {"query": query, "max_results": max_results}
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        
        try:
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"Twitter API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Twitter API error: {e}")
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose() 