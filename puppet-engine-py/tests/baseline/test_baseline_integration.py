seline Integration Tests for Puppet Engine Migration

This test suite captures the current Node.js behavior to ensure
the Python migration maintains functional parity.
port pytest
import asyncio
import httpx
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta


class TestPuppetEngineBaseline:
   Baseline tests to capture current Node.js behavior""   
    @pytest.fixture
    async def node_api_client(self):
        TP client for Node.js API"""
        async with httpx.AsyncClient(base_url=http://localhost:3000lient:
            yield client
    
    @pytest.fixture
    def test_agent_config(self) -> Dict[str, Any]:
   gent configuration
        return[object Object]
           id": "test-agent",
       name": "Test Agent",
          description: agent for baseline validation",
           personality[object Object]
             traits": ["curious", "friendly"],
             values": ["honesty", "learning"],
               speaking_style": "casual,
             interests": ["technology", "science]    },
        behavior[object Object]
               post_frequency": "2-4 hours,
               engagement_style:conversational"
            }
        }
    
    @pytest.mark.asyncio
    async def test_api_status_endpoint(self, node_api_client):
   pi/status endpoint returns expected structure""        response = await node_api_client.get("/api/status")
        assert response.status_code == 200   data = response.json()
        assertstatus" in data
        assertagents" in data
        assertuptime" in data
        assert data["status"] == "online"
        assert isinstance(data["agents"], int)
        assert isinstance(data["uptime], (int, float))
    
    @pytest.mark.asyncio
    async def test_agents_list_endpoint(self, node_api_client):
   pi/agents endpoint returns agent list""        response = await node_api_client.get("/api/agents")
        assert response.status_code == 200 agents = response.json()
        assert isinstance(agents, list)
        
        # If agents exist, validate structure
        if agents:
            agent = agents[0]
            required_fields = ["id", "name", "description, lastPostTime", "mood]         for field in required_fields:
                assert field in agent
    
    @pytest.mark.asyncio
    async def test_agent_detail_endpoint(self, node_api_client):
   Test /api/agents/:agentId endpoint"       # First get list of agents
        response = await node_api_client.get("/api/agents")
        agents = response.json()
        
        if agents:
            agent_id = agents[0]id          response = await node_api_client.get(f"/api/agents/{agent_id}")
            assert response.status_code == 200
            agent = response.json()
            required_fields =
             idame", "description", "personality", 
             styleGuide", "behavior", "currentMood,lastPostTime", "goals"
            ]
            for field in required_fields:
                assert field in agent
    
    @pytest.mark.asyncio
    async def test_agent_memory_endpoint(self, node_api_client):
   Test /api/agents/:agentId/memory endpoint"       # First get list of agents
        response = await node_api_client.get("/api/agents")
        agents = response.json()
        
        if agents:
            agent_id = agents[0]id          response = await node_api_client.get(f"/api/agents/{agent_id}/memory")
            assert response.status_code == 200
            memory = response.json()
            assert isinstance(memory, dict)
    
    @pytest.mark.asyncio
    async def test_agent_context_endpoint(self, node_api_client):
   Test /api/agents/:agentId/context endpoint"       # First get list of agents
        response = await node_api_client.get("/api/agents")
        agents = response.json()
        
        if agents:
            agent_id = agents[0]id          response = await node_api_client.get(f"/api/agents/{agent_id}/context")
            assert response.status_code == 200
            context_data = response.json()
            assert "context in context_data
            asserthasCustomPrompt in context_data
            assert isinstance(context_datacontext, str)
            assert isinstance(context_data["hasCustomPrompt], bool)
    
    @pytest.mark.asyncio
    async def test_agent_post_endpoint(self, node_api_client):
   Test /api/agents/:agentId/post endpoint"       # First get list of agents
        response = await node_api_client.get("/api/agents")
        agents = response.json()
        
        if agents:
            agent_id = agents[0]["id"]
            
            # Test with force flag to bypass time constraints
            post_data =[object Object]
            topic": "test topic,
               threadLength": 1
            force: True
            }
            
            response = await node_api_client.post(
                f"/api/agents/{agent_id}/post,              json=post_data
            )
            
            # Should either succeed (200) or be rate limited (429)
            assert response.status_code in [200, 429       if response.status_code == 200             tweet_data = response.json()
                assert isinstance(tweet_data, dict)
            elif response.status_code == 429             error_data = response.json()
                assert "error" in error_data
                assertlastPostTime" in error_data
    
    @pytest.mark.asyncio
    async def test_agent_reply_endpoint(self, node_api_client):
   Test /api/agents/:agentId/reply endpoint"       # First get list of agents
        response = await node_api_client.get("/api/agents")
        agents = response.json()
        
        if agents:
            agent_id = agents[0]["id"]
            
            reply_data =[object Object]
                tweetId": "123456789,
              content": "Test reply content"
            }
            
            response = await node_api_client.post(
                f"/api/agents/{agent_id}/reply,              json=reply_data
            )
            
            # Should succeed or return error
            assert response.status_code in [200, 400, 50       if response.status_code == 200             reply_data = response.json()
                assert isinstance(reply_data, dict)
    
    @pytest.mark.asyncio
    async def test_create_agent_endpoint(self, node_api_client, test_agent_config):
   t /api/agents POST endpoint for creating new agents""        response = await node_api_client.post(
         /api/agents",
            json=test_agent_config
        )
        
        # Should either succeed or return validation error
        assert response.status_code in [20]
        
        if response.status_code == 200:
            agent_data = response.json()
            assert agent_data["id"] == test_agent_configid            assert agent_data["name"] == test_agent_config[name"]
    
    @pytest.mark.asyncio
    async def test_events_endpoint(self, node_api_client):
   pi/events endpoint""        response = await node_api_client.get("/api/events")
        assert response.status_code == 200 events = response.json()
        assert isinstance(events, list)
    
    @pytest.mark.asyncio
    async def test_trigger_event_endpoint(self, node_api_client):
   Test /api/events/trigger endpoint"""
        event_data = {
       type": "test_event",
           data": {"message": "test event"}
        }
        
        response = await node_api_client.post(
       /api/events/trigger",
            json=event_data
        )
        
        # Should succeed or return validation error
        assert response.status_code in [200400, 500]
    
    @pytest.mark.asyncio
    async def test_memory_endpoints(self, node_api_client):
    est memory-related endpoints       # Test /api/memory endpoint
        response = await node_api_client.get("/api/memory")
        assert response.status_code == 200       memory_data = response.json()
        assert isinstance(memory_data, dict)
    
    @pytest.mark.asyncio
    async def test_llm_providers_endpoint(self, node_api_client):
      Test /api/llm/providers endpoint""        response = await node_api_client.get("/api/llm/providers")
        assert response.status_code == 200
        providers = response.json()
        assert isinstance(providers, list)
        
        # Should have at least OpenAI provider
        provider_names = [p.get("name") for p in providers]
        assert "openai" in provider_names
    
    @pytest.mark.asyncio
    async def test_llm_generate_endpoint(self, node_api_client):
         /api/llm/generate endpoint""     generate_data = {
           provider": "openai",
           prompt:Hello, this is a test prompt.",
       options[object Object]
               max_tokens": 100
                temperature:0.7         }
        }
        
        response = await node_api_client.post(
            /api/llm/generate",
            json=generate_data
        )
        
        # Should succeed or return error (depending on API key availability)
        assert response.status_code in [20]
        
        if response.status_code == 200:
            result = response.json()
            assert "content" in result
            assert isinstance(result["content"], str)
    
    @pytest.mark.asyncio
    async def test_twitter_endpoints(self, node_api_client):
     st Twitter-related endpoints       # Test /api/twitter/status endpoint
        response = await node_api_client.get("/api/twitter/status")
        assert response.status_code == 200       status_data = response.json()
        assert isinstance(status_data, dict)
        assert "connected" in status_data
    
    @pytest.mark.asyncio
    async def test_solana_endpoints(self, node_api_client):
    est Solana-related endpoints       # Test /api/solana/status endpoint
        response = await node_api_client.get("/api/solana/status")
        assert response.status_code == 200       status_data = response.json()
        assert isinstance(status_data, dict)
    
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self, node_api_client):
     t /health endpoint""        response = await node_api_client.get(/health")
        assert response.status_code == 200       health_data = response.json()
        assert status" in health_data
        assert health_data["status"] in ["healthy", unhealthy"]
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, node_api_client):
       /metrics endpoint for Prometheus metrics""        response = await node_api_client.get("/metrics")
        assert response.status_code == 20      metrics_text = response.text
        assert isinstance(metrics_text, str)
        # Should contain some metric data
        assert len(metrics_text) > 0


class TestPerformanceBaseline:
rformance baseline tests"" 
    @pytest.mark.asyncio
    async def test_api_response_time(self, node_api_client):
 TestAPI response times are within acceptable limits       import time
        
        endpoints = [
         /api/status",
         /api/agents",
           /health"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = await node_api_client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Response should be under 1 second
            assert response_time < 1.0
            assert response.status_code == 200 
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, node_api_client):
      ling of concurrent requests
        import asyncio
        
        async def make_request():
            response = await node_api_client.get("/api/status")
            return response.status_code
        
        # Make 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(status ==200 status in results)


class TestDataConsistencyBaseline:
    "nsistency baseline tests"" 
    @pytest.mark.asyncio
    async def test_agent_data_consistency(self, node_api_client):
        st that agent data is consistent across endpoints"""
        # Get agents list
        response = await node_api_client.get("/api/agents")
        agents_list = response.json()
        
        if agents_list:
            agent_id = agents_list[0]["id"]
            
            # Get agent detail
            response = await node_api_client.get(f"/api/agents/{agent_id}")
            agent_detail = response.json()
            
            # Data should be consistent
            assert agent_detailident_id
            assert agent_detail["name] == agents_list[0][name"]
    
    @pytest.mark.asyncio
    async def test_memory_data_consistency(self, node_api_client):
  t that memory data is consistent"""
        # Get agents list
        response = await node_api_client.get("/api/agents")
        agents = response.json()
        
        if agents:
            agent_id = agents[0]["id"]
            
            # Get agent memory
            response = await node_api_client.get(f"/api/agents/{agent_id}/memory")
            memory = response.json()
            
            # Memory should be associated with the correct agent
            assert "agent_id" in memory or "agentId" in memory


if __name__ == "__main__:
    pytest.main([__file__, "-v"]) 