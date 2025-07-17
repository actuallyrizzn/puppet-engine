import httpx
from typing import Dict, Any, Optional
from ..core.settings import Settings

class NodeAdapter:
    def __init__(self, settings: Settings):
        self.node_url = getattr(settings, 'node_api_url', 'http://localhost:3000')
        self.client = httpx.AsyncClient()

    async def forward_request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.node_url}{path}"
        try:
            response = await self.client.request(
                method=method,
                url=url,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Node.js API error: {e}") 