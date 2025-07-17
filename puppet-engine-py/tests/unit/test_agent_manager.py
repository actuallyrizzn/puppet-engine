"""
Tests for AgentManager
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from datetime import datetime, timedelta
import json
import tempfile
import os
from pathlib import Path

from src.agents.agent_manager import AgentManager
from src.core.models import Agent, Personality, MemoryItem, Event, Tweet, MemoryType
from src.memory.base import MemoryStore
from src.llm.base import BaseLLMProvider
from src.twitter.client import TwitterXClient
from src.events.engine import EventEngine


class TestAgentManager:
    @pytest.fixture
    def mock_memory_store(self):
        """Mock memory store"""
        store = MagicMock(spec=MemoryStore)
        store.store_memory = AsyncMock()
        return store
    
    @pytest.fixture
    def mock_llm_provider(self):
        """Mock LLM provider"""
        provider = MagicMock(spec=BaseLLMProvider)
        provider.generate_tweet = AsyncMock(return_value="Test tweet content")
        return provider
    
    @pytest.fixture
    def mock_twitter_client(self):
        """Mock Twitter client"""
        client = MagicMock(spec=TwitterXClient)
        client.post_tweet = AsyncMock(return_value={"data": {"id": "123456"}})
        return client
    
    @pytest.fixture
    def mock_event_engine(self):
        """Mock event engine"""
        engine = MagicMock(spec=EventEngine)
        engine.add_event_listener = MagicMock()
        engine.schedule_event = MagicMock()
        return engine
    
    @pytest.fixture
    def agent_manager(self, mock_memory_store, mock_llm_provider, mock_twitter_client, mock_event_engine):
        """Create AgentManager instance with mocked dependencies"""
        options = {
            'memory_store': mock_memory_store,
            'default_llm_provider': mock_llm_provider,
            'llm_providers': {'fake': mock_llm_provider},
            'twitter_client': mock_twitter_client,
            'event_engine': mock_event_engine
        }
        return AgentManager(options)
    
    @pytest.fixture
    def sample_agent_config(self):
        """Sample agent configuration"""
        return {
            "id": "test-agent",
            "name": "Test Agent",
            "description": "A test agent",
            "llm_provider": "fake",
            "is_active": True,
            "personality": {
                "traits": ["curious", "friendly"],
                "values": ["innovation"],
                "speaking_style": "casual",
                "interests": ["technology"]
            },
            "behavior": {
                "post_frequency": {
                    "min_hours_between_posts": 2,
                    "max_hours_between_posts": 6
                }
            },
            "initial_memory": {
                "core_memories": ["I am a test agent"],
                "recent_events": []
            }
        }
    
    def test_agent_manager_initialization(self, agent_manager):
        """Test AgentManager initialization"""
        assert agent_manager.agents == {}
        assert agent_manager.memory_store is not None
        assert agent_manager.default_llm_provider is not None
        assert agent_manager.twitter_client is not None
        assert agent_manager.event_engine is not None
    
    @pytest.mark.asyncio
    async def test_load_agent_success(self, agent_manager, sample_agent_config):
        """Test successful agent loading"""
        await agent_manager.load_agent(sample_agent_config)
        
        # Check agent was loaded
        assert "test-agent" in agent_manager.agents
        agent = agent_manager.agents["test-agent"]
        assert agent.id == "test-agent"
        assert agent.name == "Test Agent"
        assert agent.is_active is True
        
        # Check personality was set
        assert agent.personality.traits == ["curious", "friendly"]
        assert agent.personality.values == ["innovation"]
        
        # Check LLM provider was assigned
        assert "test-agent" in agent_manager.agent_llm_providers
    
    @pytest.mark.asyncio
    async def test_load_agent_missing_id(self, agent_manager):
        """Test agent loading with missing ID"""
        config = {"name": "Test Agent"}
        
        with pytest.raises(ValueError, match="Agent config must have an ID"):
            await agent_manager.load_agent(config)
    
    @pytest.mark.asyncio
    async def test_load_agent_with_initial_memory(self, agent_manager, sample_agent_config, mock_memory_store):
        """Test agent loading with initial memory"""
        await agent_manager.load_agent(sample_agent_config)
        
        # Check memory was initialized
        mock_memory_store.store_memory.assert_called()
        call_args = mock_memory_store.store_memory.call_args[0][0]
        assert call_args.agent_id == "test-agent"
        assert call_args.type == MemoryType.CORE
        assert call_args.content == "I am a test agent"
    
    @pytest.mark.asyncio
    async def test_get_agent(self, agent_manager, sample_agent_config):
        """Test getting agent by ID"""
        await agent_manager.load_agent(sample_agent_config)
        
        agent = agent_manager.get_agent("test-agent")
        assert agent is not None
        assert agent.id == "test-agent"
        
        # Test non-existent agent
        agent = agent_manager.get_agent("non-existent")
        assert agent is None
    
    def test_get_llm_provider_for_agent(self, agent_manager, mock_llm_provider):
        """Test getting LLM provider for agent"""
        agent_manager.agent_llm_providers["test-agent"] = mock_llm_provider
        
        provider = agent_manager.get_llm_provider_for_agent("test-agent")
        assert provider == mock_llm_provider
        
        # Test default provider
        provider = agent_manager.get_llm_provider_for_agent("unknown-agent")
        assert provider == agent_manager.default_llm_provider
    
    @pytest.mark.asyncio
    async def test_schedule_agent_posts(self, agent_manager, sample_agent_config, mock_event_engine):
        """Test scheduling agent posts"""
        await agent_manager.load_agent(sample_agent_config)
        
        await agent_manager.schedule_agent_posts("test-agent")
        
        # Check event was scheduled
        mock_event_engine.schedule_event.assert_called()
        event = mock_event_engine.schedule_event.call_args[0][0]
        assert event.type == "agent_post"
        assert event.agent_id == "test-agent"
    
    @pytest.mark.asyncio
    async def test_schedule_agent_posts_inactive_agent(self, agent_manager, sample_agent_config):
        """Test scheduling posts for inactive agent"""
        sample_agent_config["is_active"] = False
        await agent_manager.load_agent(sample_agent_config)
        
        await agent_manager.schedule_agent_posts("test-agent")
        
        # Should not schedule anything for inactive agent
        assert "test-agent" not in agent_manager.next_post_times
    
    @pytest.mark.asyncio
    async def test_create_agent_post_success(self, agent_manager, sample_agent_config, mock_llm_provider, mock_twitter_client):
        """Test successful agent post creation"""
        await agent_manager.load_agent(sample_agent_config)
        
        tweet = await agent_manager.create_agent_post("test-agent")
        
        assert tweet is not None
        assert tweet.text == "Test tweet content"
        assert tweet.agent_id == "test-agent"
        assert tweet.twitter_id == "123456"
        
        # Check LLM was called
        mock_llm_provider.generate_tweet.assert_called()
        
        # Check Twitter was called
        mock_twitter_client.post_tweet.assert_called_with("Test tweet content")
        
        # Check memory was stored
        agent_manager.memory_store.store_memory.assert_called()
    
    @pytest.mark.asyncio
    async def test_create_agent_post_inactive_agent(self, agent_manager, sample_agent_config):
        """Test creating post for inactive agent"""
        sample_agent_config["is_active"] = False
        await agent_manager.load_agent(sample_agent_config)
        
        tweet = await agent_manager.create_agent_post("test-agent")
        
        assert tweet is None
    
    @pytest.mark.asyncio
    async def test_create_agent_post_no_llm_provider(self, agent_manager, sample_agent_config):
        """Test creating post without LLM provider"""
        # Set default provider to None and clear agent providers
        agent_manager.default_llm_provider = None
        agent_manager.agent_llm_providers = {}
        await agent_manager.load_agent(sample_agent_config)
        
        tweet = await agent_manager.create_agent_post("test-agent")
        
        # When no LLM provider is set, a fake provider is used as fallback
        assert tweet is not None
        assert "Test tweet content" in tweet.text
    
    @pytest.mark.asyncio
    async def test_create_agent_post_twitter_error(self, agent_manager, sample_agent_config, mock_twitter_client):
        """Test creating post with Twitter API error"""
        await agent_manager.load_agent(sample_agent_config)
        
        # Mock Twitter error
        mock_twitter_client.post_tweet.side_effect = Exception("Twitter API error")
        
        tweet = await agent_manager.create_agent_post("test-agent")
        
        assert tweet is None
        assert agent_manager.api_error_counts["test-agent"] == 1
    
    @pytest.mark.asyncio
    async def test_process_agent_reaction(self, agent_manager, sample_agent_config, mock_llm_provider, mock_twitter_client):
        """Test processing agent reaction to tweet"""
        await agent_manager.load_agent(sample_agent_config)
        
        tweet_data = {
            "id": "123456",
            "text": "Hello @test-agent, how are you?",
            "author_id": "user123"
        }
        
        await agent_manager.process_agent_reaction("test-agent", tweet_data)
        
        # Check tweet was processed
        assert "123456" in agent_manager.processed_tweet_ids
        
        # Check response was generated and posted
        mock_llm_provider.generate_tweet.assert_called()
        mock_twitter_client.post_tweet.assert_called()
        
        # Check memory was stored
        agent_manager.memory_store.store_memory.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_agent_reaction_duplicate_tweet(self, agent_manager, sample_agent_config):
        """Test processing duplicate tweet"""
        await agent_manager.load_agent(sample_agent_config)
        
        tweet_data = {"id": "123456", "text": "Test tweet"}
        
        # Process same tweet twice
        await agent_manager.process_agent_reaction("test-agent", tweet_data)
        await agent_manager.process_agent_reaction("test-agent", tweet_data)
        
        # Should only process once
        assert len(agent_manager.processed_tweet_ids) == 1
    
    @pytest.mark.asyncio
    async def test_process_agent_event(self, agent_manager, sample_agent_config, mock_llm_provider, mock_twitter_client):
        """Test processing agent event"""
        await agent_manager.load_agent(sample_agent_config)
        
        event = Event(
            type="news_event",
            data={"content": "Breaking news: AI breakthrough!"}
        )
        
        await agent_manager.process_agent_event("test-agent", event)
        
        # Check LLM was called for news reaction
        mock_llm_provider.generate_tweet.assert_called()
        
        # Check memory was stored
        agent_manager.memory_store.store_memory.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_agent_event_mood_change(self, agent_manager, sample_agent_config):
        """Test processing mood event"""
        await agent_manager.load_agent(sample_agent_config)
        
        agent = agent_manager.get_agent("test-agent")
        original_mood = agent.current_mood.copy()
        
        event = Event(
            type="mood_event",
            agent_id="test-agent",
            data={"mood": {"excitement": 0.8}}
        )
        
        await agent_manager.process_agent_event("test-agent", event)
        
        # Check mood was updated
        assert agent.current_mood["excitement"] == 0.8
        assert agent.current_mood != original_mood
    
    @pytest.mark.asyncio
    async def test_start_stop_streaming_mentions(self, agent_manager, sample_agent_config):
        """Test starting and stopping streaming mentions"""
        await agent_manager.load_agent(sample_agent_config)
        
        # Start streaming
        await agent_manager.start_streaming_mentions()
        assert agent_manager.is_streaming is True
        assert len(agent_manager.streaming_tasks) == 1
        
        # Stop streaming
        await agent_manager.stop_streaming_mentions()
        assert agent_manager.is_streaming is False
        assert len(agent_manager.streaming_tasks) == 0
    
    @pytest.mark.asyncio
    async def test_start_streaming_no_twitter_client(self, agent_manager, sample_agent_config):
        """Test starting streaming without Twitter client"""
        agent_manager.twitter_client = None
        await agent_manager.load_agent(sample_agent_config)
        
        await agent_manager.start_streaming_mentions()
        
        assert agent_manager.is_streaming is False
        assert len(agent_manager.streaming_tasks) == 0
    
    def test_get_agent_status(self, agent_manager, sample_agent_config):
        """Test getting agent status"""
        # Load agent
        asyncio.run(agent_manager.load_agent(sample_agent_config))
        
        status = agent_manager.get_agent_status("test-agent")
        
        assert status["id"] == "test-agent"
        assert status["name"] == "Test Agent"
        assert status["is_active"] is True
        assert status["api_error_count"] == 0
        assert status["api_cooldown_until"] is None
    
    def test_get_agent_status_not_found(self, agent_manager):
        """Test getting status for non-existent agent"""
        status = agent_manager.get_agent_status("non-existent")
        
        assert status["error"] == "Agent not found"
    
    def test_get_all_agents_status(self, agent_manager, sample_agent_config):
        """Test getting status for all agents"""
        # Load agent
        asyncio.run(agent_manager.load_agent(sample_agent_config))
        
        all_status = agent_manager.get_all_agents_status()
        
        assert "test-agent" in all_status
        assert all_status["test-agent"]["id"] == "test-agent"
    
    @pytest.mark.asyncio
    async def test_load_agents_from_directory(self, agent_manager, sample_agent_config):
        """Test loading agents from directory"""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_agent_config, f)
            config_path = f.name
        
        try:
            # Mock Path.exists to return True
            with patch('pathlib.Path.exists') as mock_exists:
                mock_exists.return_value = True
                
                # Mock Path.glob to return our config file
                with patch('pathlib.Path.glob') as mock_glob:
                    mock_glob.return_value = [Path(config_path)]
                    
                    # Mock json.load to return our config
                    with patch('json.load') as mock_json_load:
                        mock_json_load.return_value = sample_agent_config
                        
                        await agent_manager.load_agents("fake_config_dir")
                        
                        # Check agent was loaded
                        assert "test-agent" in agent_manager.agents
        finally:
            # Clean up
            os.unlink(config_path)
    
    @pytest.mark.asyncio
    async def test_load_agents_directory_not_found(self, agent_manager):
        """Test loading agents from non-existent directory"""
        await agent_manager.load_agents("non_existent_dir")
        
        # Should not raise error, just log and return
        assert len(agent_manager.agents) == 0
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, agent_manager, sample_agent_config):
        """Test API error handling with exponential backoff"""
        await agent_manager.load_agent(sample_agent_config)
        
        # Simulate API errors
        await agent_manager._handle_api_error("test-agent", Exception("API Error 1"))
        await agent_manager._handle_api_error("test-agent", Exception("API Error 2"))
        
        assert agent_manager.api_error_counts["test-agent"] == 2
        
        # Check cooldown was set
        cooldown = agent_manager.api_cooldowns["test-agent"]
        assert cooldown > datetime.utcnow()
    
    @pytest.mark.asyncio
    async def test_event_listener_setup(self, agent_manager, mock_event_engine):
        """Test event listener setup"""
        # Event listeners should be set up during initialization
        mock_event_engine.add_event_listener.assert_called()
        
        # Check all expected event types were registered
        calls = mock_event_engine.add_event_listener.call_args_list
        event_types = [call[0][0] for call in calls]
        expected_types = ["agent_post", "news_event", "mood_event", "interaction_event"]
        
        for event_type in expected_types:
            assert event_type in event_types 