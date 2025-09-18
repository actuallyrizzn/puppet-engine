"""
Puppet Engine - Main Entry Point

A real-time AI agent framework for deploying autonomous characters on Twitter
who communicate, evolve, and perform unscripted social behavior.
"""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from .core.settings import Settings
from .memory.sqlite_store import SQLiteMemoryStore
from .llm.openai_provider import OpenAILLMProvider
from .llm.fake_provider import FakeLLMProvider
from .twitter.client import TwitterXClient
from .events.engine import EventEngine
from .agents.agent_manager import AgentManager
from .api.server import APIServer
from .utils.observability import setup_observability, StructuredLogger


class PuppetEngine:
    def __init__(self):
        self.settings = Settings()
        self.logger = StructuredLogger("puppet-engine")
        self.components: Dict[str, Any] = {}
        self.is_running = False
        self._periodic_tasks = []  # Track periodic event tasks
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the Puppet Engine"""
        self.logger.log("info", "Starting Puppet Engine...")
        
        try:
            # Initialize SQLite memory store
            memory_store = SQLiteMemoryStore()
            self.logger.log("info", "Using SQLite memory store")
            
            # Initialize Twitter client
            twitter_credentials = {
                'api_key': self.settings.twitter_api_key,
                'api_secret': self.settings.twitter_api_secret,
                'access_token': self.settings.twitter_access_token,
                'access_token_secret': self.settings.twitter_access_token_secret,
                'bearer_token': self.settings.twitter_bearer_token
            }
            
            # Filter out None values
            twitter_credentials = {k: v for k, v in twitter_credentials.items() if v is not None}
            
            twitter_client = TwitterXClient(twitter_credentials)
            self.logger.log("info", "Twitter client initialized")
            
            # Initialize LLM providers
            llm_providers = {}
            default_provider = None
            
            # OpenAI provider
            if self.settings.openai_api_key:
                openai_provider = OpenAILLMProvider({
                    'api_key': self.settings.openai_api_key,
                    'model': self.settings.openai_model
                })
                llm_providers['openai'] = openai_provider
                default_provider = openai_provider
                self.logger.log("info", "OpenAI provider initialized")
            
            # Fake provider as fallback
            fake_provider = FakeLLMProvider({
                'model': 'fake-model',
                'temperature': 0.7
            })
            llm_providers['fake'] = fake_provider
            
            if not default_provider:
                default_provider = fake_provider
                self.logger.log("info", "Using fake LLM provider as default")
            
            self.logger.log("info", "LLM providers initialized")
            
            # Initialize event engine
            event_engine = EventEngine()
            self.logger.log("info", "Event engine initialized")
            
            # Initialize agent manager
            agent_manager = AgentManager({
                'memory_store': memory_store,
                'default_llm_provider': default_provider,
                'llm_providers': llm_providers,
                'twitter_client': twitter_client,
                'event_engine': event_engine,
                'settings': self.settings
            })
            self.logger.log("info", "Agent manager initialized")
            
            # Load agents from configuration
            await agent_manager.load_agents()
            
            # Initialize API server
            api_server = APIServer(self.settings)
            self.logger.log("info", "API server initialized")
            
            # Store components
            self.components = {
                'twitter_client': twitter_client,
                'llm_providers': llm_providers,
                'memory_store': memory_store,
                'event_engine': event_engine,
                'agent_manager': agent_manager,
                'api_server': api_server,
                'file_store_active': True
            }
            
            return self.components
            
        except Exception as error:
            self.logger.log("error", f"Error initializing Puppet Engine: {error}")
            raise error
    
    async def start(self) -> None:
        """Start the Puppet Engine"""
        try:
            # Initialize components
            components = await self.initialize()
            
            # Start event engine
            event_engine = components['event_engine']
            await event_engine.start()
            
            # API server app is created; serve with uvicorn in production via separate process
            self.logger.log("info", f"API server app initialized. Serve via uvicorn on port {getattr(self.settings, 'port', 8000)}")
            
            # Start real-time streaming for Twitter mentions
            agent_manager = components['agent_manager']
            await agent_manager.start_streaming_mentions()
            
            # Set up periodic events
            agent_ids = list(agent_manager.agents.keys())
            if agent_ids:
                self._setup_periodic_events(event_engine, agent_ids)
            
            self.is_running = True
            
            # Log startup completion
            self.logger.log("info", "Puppet Engine started successfully. 🎭")
            self.logger.log("info", f"File-backed storage: {'ACTIVE' if components['file_store_active'] else 'INACTIVE'}")
            
            # Keep the engine running
            while self.is_running:
                await asyncio.sleep(1)
                
        except Exception as error:
            self.logger.log("error", f"Failed to start Puppet Engine: {error}")
            raise error
    
    def _setup_periodic_events(self, event_engine: EventEngine, agent_ids: list) -> None:
        """Set up periodic events for agents"""
        import random
        from datetime import datetime, timedelta
        from .core.models import Event
        
        # News events every 6 hours
        news_interval = getattr(self.settings, 'news_event_interval', 6 * 60 * 60)  # 6 hours in seconds
        
        # Mood events every 4 hours
        mood_interval = getattr(self.settings, 'mood_event_interval', 4 * 60 * 60)  # 4 hours in seconds
        
        # Interaction events every 8 hours
        interaction_interval = getattr(self.settings, 'interaction_event_interval', 8 * 60 * 60)  # 8 hours in seconds
        
        async def schedule_news_event():
            while self.is_running:
                await asyncio.sleep(news_interval)
                if self.is_running:
                    news_content = self._generate_random_news()
                    news_event = Event(
                        type="news_event",
                        data={"content": news_content}
                    )
                    event_engine.queue_event(news_event)
        
        async def schedule_mood_event():
            while self.is_running:
                await asyncio.sleep(mood_interval)
                if self.is_running:
                    for agent_id in agent_ids:
                        mood_event = Event(
                            type="mood_event",
                            agent_id=agent_id,
                            data={"mood": self._generate_random_mood()}
                        )
                        event_engine.queue_event(mood_event)
        
        async def schedule_interaction_event():
            while self.is_running:
                await asyncio.sleep(interaction_interval)
                if self.is_running and len(agent_ids) >= 2:
                    # Random interaction between two agents
                    agent1, agent2 = random.sample(agent_ids, 2)
                    interaction_event = Event(
                        type="interaction_event",
                        agent_id=agent1,
                        data={"target_agent": agent2, "interaction_type": "mention"}
                    )
                    event_engine.queue_event(interaction_event)
        
        # Start periodic event tasks and track them
        t1 = asyncio.create_task(schedule_news_event())
        t2 = asyncio.create_task(schedule_mood_event())
        t3 = asyncio.create_task(schedule_interaction_event())
        self._periodic_tasks.extend([t1, t2, t3])
        self.logger.log("info", f"Started periodic event tasks: {[str(t) for t in self._periodic_tasks]}")
    
    def _generate_random_news(self) -> str:
        """Generate random news content"""
        news_items = [
            "Breaking: New AI breakthrough in natural language processing",
            "Tech giants announce collaboration on open-source AI",
            "Cryptocurrency market sees significant movement",
            "Social media platforms update their algorithms",
            "Scientists discover new applications for blockchain technology",
            "Startup raises millions in funding for AI-powered solution",
            "Government announces new regulations for digital platforms",
            "Major tech conference announces groundbreaking speakers",
            "Open source community releases revolutionary new tool",
            "Industry experts predict major shifts in technology landscape"
        ]
        import random
        return random.choice(news_items)
    
    def _generate_random_mood(self) -> Dict[str, float]:
        """Generate random mood for agents"""
        import random
        moods = {
            'excitement': random.uniform(0.0, 1.0),
            'curiosity': random.uniform(0.3, 1.0),
            'skepticism': random.uniform(0.0, 0.8),
            'optimism': random.uniform(0.2, 1.0),
            'concern': random.uniform(0.0, 0.6)
        }
        return moods
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the Puppet Engine"""
        self.logger.log("info", "Shutting down Puppet Engine...")
        self.is_running = False
        
        try:
            # Stop periodic event tasks
            for task in self._periodic_tasks:
                if not task.done():
                    task.cancel()
            for task in self._periodic_tasks:
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            print(f"[PuppetEngine] Cleaned up {len(self._periodic_tasks)} periodic event tasks.")
            self._periodic_tasks.clear()
            
            # Stop streaming mentions
            if 'agent_manager' in self.components:
                await self.components['agent_manager'].stop_streaming_mentions()
            
            # Stop event engine
            if 'event_engine' in self.components:
                await self.components['event_engine'].stop()
            
            # Close Twitter client
            if 'twitter_client' in self.components:
                await self.components['twitter_client'].close()
            
            # Close SQLite connection
            if 'memory_store' in self.components and self.components['memory_store']:
                if hasattr(self.components['memory_store'], 'client'):
                    self.components['memory_store'].client.close()
            
            self.logger.log("info", "Puppet Engine shut down successfully")
            
        except Exception as error:
            self.logger.log("error", f"Error during shutdown: {error}")


# Global engine instance for signal handling
engine_instance: Optional[PuppetEngine] = None


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global engine_instance
    if engine_instance:
        asyncio.create_task(engine_instance.shutdown())


async def main():
    """Main entry point"""
    global engine_instance
    
    # Create engine instance
    engine_instance = PuppetEngine()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the engine
        await engine_instance.start()
    except KeyboardInterrupt:
        if engine_instance and engine_instance.logger:
            engine_instance.logger.log("info", "Received interrupt signal")
    except Exception as error:
        if engine_instance and engine_instance.logger:
            engine_instance.logger.log("error", f"Error in main: {error}")
        sys.exit(1)
    finally:
        # Ensure cleanup
        if engine_instance:
            await engine_instance.shutdown()


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main()) 