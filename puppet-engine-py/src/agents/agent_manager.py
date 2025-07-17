"""
Agent Manager for Puppet Engine
Handles loading, managing, and controlling agent behavior
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path

from ..core.models import Agent, Personality, MemoryItem, Event, Tweet, MemoryType
from ..memory.base import MemoryStore
from ..llm.base import BaseLLMProvider
from ..twitter.client import TwitterXClient
from ..events.engine import EventEngine
from ..core.settings import Settings


class AgentManager:
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        options = options or {}
        self.agents: Dict[str, Agent] = {}
        self.memory_store: Optional[MemoryStore] = options.get('memory_store')
        self.default_llm_provider: Optional[BaseLLMProvider] = options.get('default_llm_provider')
        self.llm_providers: Dict[str, BaseLLMProvider] = options.get('llm_providers', {})
        self.agent_llm_providers: Dict[str, BaseLLMProvider] = {}
        self.twitter_client: Optional[TwitterXClient] = options.get('twitter_client')
        self.event_engine: Optional[EventEngine] = options.get('event_engine')
        self.settings: Settings = options.get('settings', Settings())
        
        # Post scheduling and timing
        self.last_post_time: Dict[str, datetime] = {}
        self.next_post_times: Dict[str, datetime] = {}
        self.post_schedules: Dict[str, Any] = {}
        
        # Twitter API error tracking
        self.api_error_counts: Dict[str, int] = {}
        self.api_cooldowns: Dict[str, datetime] = {}
        self.processed_tweet_ids: set = set()
        
        # Streaming and real-time
        self.streaming_tasks: Dict[str, asyncio.Task] = {}
        self.is_streaming = False
        
        # Setup event listeners
        if self.event_engine:
            self._setup_event_listeners()
    
    async def load_agents(self, config_dir: str = "config/agents") -> None:
        """Load agents from configuration files"""
        try:
            config_path = Path(config_dir)
            if not config_path.exists():
                print(f"Config directory {config_dir} not found")
                return
            
            # Get all agent config files
            config_files = list(config_path.glob("*.json"))
            
            # Load each agent
            for config_file in config_files:
                with open(config_file, 'r', encoding='utf-8') as f:
                    agent_config = json.load(f)
                    await self.load_agent(agent_config)
            
            print(f"Loaded {len(self.agents)} agents")
        except Exception as error:
            print(f"Error loading agents: {error}")
            raise error
    
    async def load_agent(self, config: Dict[str, Any]) -> None:
        """Load a single agent from configuration"""
        try:
            if not config.get('id'):
                raise ValueError("Agent config must have an ID")
            
            # Create new agent
            agent = Agent(
                id=config['id'],
                name=config.get('name', config['id']),
                description=config.get('description', ''),
                custom_system_prompt=config.get('custom_system_prompt'),
                rotating_system_prompts=config.get('rotating_system_prompts', []),
                behavior=config.get('behavior', {}),
                is_active=config.get('is_active', True)
            )
            
            # Set up personality
            if config.get('personality'):
                personality_config = config['personality']
                agent.personality = Personality(
                    traits=personality_config.get('traits', []),
                    values=personality_config.get('values', []),
                    speaking_style=personality_config.get('speaking_style'),
                    interests=personality_config.get('interests', [])
                )
            
            # Set agent's LLM provider
            if config.get('llm_provider'):
                provider_name = config['llm_provider'].lower()
                if provider_name in self.llm_providers:
                    provider = self.llm_providers[provider_name]
                    if provider:
                        self.agent_llm_providers[agent.id] = provider
                        print(f"Using {provider_name} provider for agent {agent.id}")
                    else:
                        print(f"LLM provider {provider_name} is None for agent {agent.id}, using default")
                        if self.default_llm_provider:
                            self.agent_llm_providers[agent.id] = self.default_llm_provider
                else:
                    print(f"LLM provider {provider_name} not found for agent {agent.id}, using default")
                    if self.default_llm_provider:
                        self.agent_llm_providers[agent.id] = self.default_llm_provider
            else:
                if self.default_llm_provider:
                    self.agent_llm_providers[agent.id] = self.default_llm_provider
            
            # Initialize memory
            if self.memory_store:
                if config.get('initial_memory'):
                    await self._initialize_agent_memory(agent.id, config['initial_memory'])
            
            # Register agent-specific Twitter client if credentials provided
            if config.get('twitter_credentials'):
                print(f"Registering Twitter client for agent {agent.id}")
                # Note: Twitter client registration would be implemented here
            
            # Store agent
            self.agents[agent.id] = agent
            
            # Schedule initial posts
            await self.schedule_agent_posts(agent.id)
            
            print(f"Agent {agent.id} loaded successfully")
            
        except Exception as error:
            print(f"Error loading agent {config.get('id', 'unknown')}: {error}")
            raise error
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def get_llm_provider_for_agent(self, agent_id: str) -> Optional[BaseLLMProvider]:
        """Get the LLM provider for a specific agent"""
        return self.agent_llm_providers.get(agent_id, self.default_llm_provider)
    
    async def schedule_agent_posts(self, agent_id: str) -> None:
        """Schedule posts for an agent based on their behavior configuration"""
        agent = self.get_agent(agent_id)
        if not agent or not agent.is_active:
            return
        
        behavior = agent.behavior.get('post_frequency', {})
        min_hours = behavior.get('min_hours_between_posts', 3)
        max_hours = behavior.get('max_hours_between_posts', 12)
        
        # Calculate next post time
        now = datetime.utcnow()
        if agent_id in self.last_post_time:
            last_post = self.last_post_time[agent_id]
            min_delay = timedelta(hours=min_hours)
            if now - last_post < min_delay:
                # Still in cooldown period
                return
        
        # Schedule next post
        await self.schedule_next_post(agent_id, min_hours, max_hours)
    
    async def schedule_next_post(self, agent_id: str, min_hours: int = 3, max_hours: int = 12) -> None:
        """Schedule the next post for an agent"""
        import random
        
        # Calculate random delay within bounds
        delay_hours = random.uniform(min_hours, max_hours)
        delay_seconds = int(delay_hours * 3600)
        
        next_post_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
        self.next_post_times[agent_id] = next_post_time
        
        # Schedule the post
        if self.event_engine:
            post_event = Event(
                type="agent_post",
                agent_id=agent_id,
                data={"scheduled_time": next_post_time.isoformat()},
                scheduled_for=next_post_time
            )
            self.event_engine.schedule_event(post_event)
        
        print(f"Scheduled next post for {agent_id} at {next_post_time}")
    
    async def create_agent_post(self, agent_id: str, options: Optional[Dict[str, Any]] = None) -> Optional[Tweet]:
        """Create and post content for an agent"""
        options = options or {}
        agent = self.get_agent(agent_id)
        if not agent or not agent.is_active:
            return None
        
        try:
            # Get LLM provider
            llm_provider = self.get_llm_provider_for_agent(agent_id)
            if not llm_provider:
                print(f"No LLM provider available for agent {agent_id}")
                return None
            
            # Generate tweet content
            tweet_content = await llm_provider.generate_tweet(agent, options.get('prompt', ''))
            
            # Post to Twitter
            if self.twitter_client:
                try:
                    response = await self.twitter_client.post_tweet(tweet_content)
                    
                    # Create tweet record
                    tweet = Tweet(
                        text=tweet_content,
                        agent_id=agent_id,
                        twitter_id=response.get('data', {}).get('id'),
                        posted_at=datetime.utcnow()
                    )
                    
                    # Update agent state
                    agent.last_post_time = datetime.utcnow()
                    self.last_post_time[agent_id] = agent.last_post_time
                    
                    # Store in memory
                    if self.memory_store:
                        memory_item = MemoryItem(
                            agent_id=agent_id,
                            type=MemoryType.GENERAL,
                            content=tweet_content,
                            metadata={"twitter_id": tweet.twitter_id, "memory_type": "tweet"}
                        )
                        await self.memory_store.store_memory(memory_item)
                    
                    # Schedule next post
                    await self.schedule_agent_posts(agent_id)
                    
                    print(f"Agent {agent_id} posted: {tweet_content[:50]}...")
                    return tweet
                    
                except Exception as e:
                    await self._handle_api_error(agent_id, e)
                    return None
            
        except Exception as error:
            print(f"Error creating post for agent {agent_id}: {error}")
            return None
    
    async def process_agent_reaction(self, agent_id: str, tweet_data: Dict[str, Any]) -> None:
        """Process a mention or interaction for an agent"""
        agent = self.get_agent(agent_id)
        if not agent or not agent.is_active:
            return
        
        try:
            # Check if we've already processed this tweet
            tweet_id = tweet_data.get('id')
            if not tweet_id or tweet_id in self.processed_tweet_ids:
                return
            
            self.processed_tweet_ids.add(tweet_id)
            
            # Get conversation context
            conversation_history = await self._fetch_conversation_thread(
                str(tweet_id), [], agent_id
            )
            
            # Generate response
            llm_provider = self.get_llm_provider_for_agent(agent_id)
            if llm_provider:
                # Create response prompt with context
                prompt = self._create_response_prompt(agent, tweet_data, conversation_history)
                response_content = await llm_provider.generate_tweet(agent, prompt)
                
                # Post response
                if self.twitter_client:
                    await self.twitter_client.post_tweet(response_content, reply_to=str(tweet_id))
                    
                    # Store interaction in memory
                    if self.memory_store:
                        memory_item = MemoryItem(
                            agent_id=agent_id,
                            type=MemoryType.INTERACTION,
                            content=f"Replied to tweet {tweet_id}: {response_content}",
                            metadata={"original_tweet": tweet_data, "response": response_content}
                        )
                        await self.memory_store.store_memory(memory_item)
                    
                    print(f"Agent {agent_id} replied to tweet {tweet_id}")
            
        except Exception as error:
            print(f"Error processing reaction for agent {agent_id}: {error}")
    
    async def process_agent_event(self, agent_id: str, event: Event) -> None:
        """Process an event for an agent"""
        agent = self.get_agent(agent_id)
        if not agent or not agent.is_active:
            return
        
        try:
            event_type = event.type
            
            if event_type == "agent_post":
                # Handle scheduled post
                await self.create_agent_post(agent_id)
            
            elif event_type == "news_event":
                # Handle news event
                news_content = event.data.get('content', '')
                if news_content:
                    # Generate reaction to news
                    llm_provider = self.get_llm_provider_for_agent(agent_id)
                    if llm_provider:
                        prompt = f"React to this news: {news_content}"
                        response = await llm_provider.generate_tweet(agent, prompt)
                        
                        if self.twitter_client:
                            await self.twitter_client.post_tweet(response)
            
            elif event_type == "mood_event":
                # Handle mood change
                new_mood = event.data.get('mood', {})
                agent.current_mood.update(new_mood)
            
            # Store event in memory
            if self.memory_store:
                memory_item = MemoryItem(
                    agent_id=agent_id,
                    type=MemoryType.EVENT,
                    content=f"Processed {event_type} event",
                    metadata={"event_data": event.data}
                )
                await self.memory_store.store_memory(memory_item)
            
        except Exception as error:
            print(f"Error processing event for agent {agent_id}: {error}")
    
    async def start_streaming_mentions(self) -> None:
        """Start real-time streaming of mentions for all agents"""
        if not self.twitter_client or self.is_streaming:
            return
        
        self.is_streaming = True
        
        # Start streaming for each agent
        for agent_id in self.agents.keys():
            if self.agents[agent_id].is_active:
                task = asyncio.create_task(self._stream_mentions_for_agent(agent_id))
                self.streaming_tasks[agent_id] = task
        
        print("Started streaming mentions for all agents")
    
    async def stop_streaming_mentions(self) -> None:
        """Stop real-time streaming of mentions"""
        self.is_streaming = False
        
        # Cancel all streaming tasks
        for task in self.streaming_tasks.values():
            task.cancel()
        
        self.streaming_tasks.clear()
        print("Stopped streaming mentions")
    
    async def _stream_mentions_for_agent(self, agent_id: str) -> None:
        """Stream mentions for a specific agent"""
        while self.is_streaming:
            try:
                # Get mentions for agent
                mentions = await self._get_agent_mentions(agent_id)
                
                for mention in mentions:
                    await self.process_agent_reaction(agent_id, mention)
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as error:
                print(f"Error streaming mentions for agent {agent_id}: {error}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def _get_agent_mentions(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get mentions for an agent (placeholder implementation)"""
        # This would integrate with Twitter API to get real mentions
        # For now, return empty list
        return []
    
    async def _fetch_conversation_thread(self, tweet_id: str, conversation_history: List[Dict], 
                                       agent_id: str, depth: int = 0, max_depth: int = 5) -> List[Dict]:
        """Fetch conversation thread for context"""
        if depth >= max_depth:
            return conversation_history
        
        # This would fetch the actual conversation thread from Twitter API
        # For now, return the provided history
        return conversation_history
    
    def _create_response_prompt(self, agent: Agent, tweet_data: Dict[str, Any], 
                              conversation_history: List[Dict]) -> str:
        """Create a prompt for generating a response"""
        tweet_text = tweet_data.get('text', '')
        
        prompt = f"""
        You are {agent.name}. Someone tweeted at you: "{tweet_text}"
        
        Respond in your unique voice and style. Be authentic to your personality.
        Keep your response engaging and true to your character.
        """
        
        return prompt
    
    async def _initialize_agent_memory(self, agent_id: str, initial_memory: Dict[str, Any]) -> None:
        """Initialize an agent's memory with initial data"""
        if not self.memory_store:
            return
        
        # Add core memories
        if initial_memory.get('core_memories'):
            for content in initial_memory['core_memories']:
                memory_item = MemoryItem(
                    agent_id=agent_id,
                    type=MemoryType.CORE,
                    content=content,
                    importance=1.0
                )
                await self.memory_store.store_memory(memory_item)
        
        # Add recent events
        if initial_memory.get('recent_events'):
            for event in initial_memory['recent_events']:
                memory_item = MemoryItem(
                    agent_id=agent_id,
                    type=MemoryType.EVENT,
                    content=event.get('content', str(event)),
                    importance=event.get('importance', 0.7)
                )
                await self.memory_store.store_memory(memory_item)
    
    async def _handle_api_error(self, agent_id: str, error: Exception) -> None:
        """Handle API errors with exponential backoff"""
        self.api_error_counts[agent_id] = self.api_error_counts.get(agent_id, 0) + 1
        
        # Calculate cooldown time (exponential backoff)
        cooldown_minutes = min(2 ** self.api_error_counts[agent_id], 60)  # Max 1 hour
        cooldown_end = datetime.utcnow() + timedelta(minutes=cooldown_minutes)
        self.api_cooldowns[agent_id] = cooldown_end
        
        print(f"API error for agent {agent_id}: {error}. Cooldown until {cooldown_end}")
    
    def _setup_event_listeners(self) -> None:
        """Setup event listeners for the event engine"""
        if not self.event_engine:
            return
        
        # Listen for agent events
        self.event_engine.add_event_listener("agent_post", self._handle_agent_post_event)
        self.event_engine.add_event_listener("news_event", self._handle_news_event)
        self.event_engine.add_event_listener("mood_event", self._handle_mood_event)
        self.event_engine.add_event_listener("interaction_event", self._handle_interaction_event)
    
    async def _handle_agent_post_event(self, event: Event) -> None:
        """Handle agent post events"""
        if event.agent_id:
            await self.create_agent_post(event.agent_id)
    
    async def _handle_news_event(self, event: Event) -> None:
        """Handle news events for all agents"""
        for agent_id in self.agents.keys():
            if self.agents[agent_id].is_active:
                await self.process_agent_event(agent_id, event)
    
    async def _handle_mood_event(self, event: Event) -> None:
        """Handle mood events for all agents"""
        for agent_id in self.agents.keys():
            if self.agents[agent_id].is_active:
                await self.process_agent_event(agent_id, event)
    
    async def _handle_interaction_event(self, event: Event) -> None:
        """Handle interaction events between agents"""
        agent_id = event.agent_id
        if agent_id and agent_id in self.agents:
            await self.process_agent_event(agent_id, event)
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status information for an agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return {"error": "Agent not found"}
        
        next_post_time = self.next_post_times.get(agent_id)
        api_cooldown = self.api_cooldowns.get(agent_id)
        
        return {
            "id": agent.id,
            "name": agent.name,
            "is_active": agent.is_active,
            "last_post_time": agent.last_post_time.isoformat() if agent.last_post_time else None,
            "next_post_time": next_post_time.isoformat() if next_post_time else None,
            "api_error_count": self.api_error_counts.get(agent_id, 0),
            "api_cooldown_until": api_cooldown.isoformat() if api_cooldown else None
        }
    
    def get_all_agents_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all agents"""
        return {agent_id: self.get_agent_status(agent_id) for agent_id in self.agents.keys()} 