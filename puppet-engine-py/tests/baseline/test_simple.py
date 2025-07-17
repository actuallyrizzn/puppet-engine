import pytest
import httpx


class TestSimpleBaseline:
    @pytest.fixture
    async def node_api_client(self):
        async with httpx.AsyncClient(base_url=http://localhost:3000lient:
            yield client
    
    @pytest.mark.asyncio
    async def test_api_status_endpoint(self, node_api_client):
        response = await node_api_client.get("/api/status")
        assert response.status_code == 200   data = response.json()
        assertstatus" in data
        assertagents" in data
        assertuptime 