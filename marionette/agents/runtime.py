import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from ..types import Agent, MemoryItem, Relationship, Event
from ..llm.client import llm_client
from ..events.router import event_router
from ..events.handlers import EVENT_TYPES

class AgentRuntime:
    """Core runtime for agent behavior and interactions."""
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.mood = {
            "positivity": 0.5,  # Neutral starting point
            "energy": 0.5,
            "formality": 0.5
        }
        self.last_interaction = datetime.utcnow()
        self._interaction_lock = asyncio.Lock()
    
    async def process_memory(self, memory: MemoryItem) -> None:
        """Process a new memory and update agent state."""
        async with self._interaction_lock:
            # Analyze memory sentiment
            sentiment = await llm_client.analyze_sentiment(memory.content)
            
            # Update mood with weighted average
            for key in self.mood:
                self.mood[key] = (self.mood[key] * 0.7 + sentiment[key] * 0.3)
            
            # Dispatch mood change event
            await event_router.dispatch_event(Event(
                type=EVENT_TYPES["MOOD_CHANGED"],
                agent_id=self.agent.id,
                data={
                    "old_mood": self.mood.copy(),
                    "new_mood": sentiment,
                    "trigger": memory.content
                }
            ))
    
    async def generate_response(self, context: str, memories: List[MemoryItem]) -> str:
        """Generate a response based on context and memories."""
        async with self._interaction_lock:
            # Generate memory summary
            memory_summary = await llm_client.generate_memory_summary(memories)
            
            # Generate agent prompt
            prompt = await llm_client.generate_agent_prompt(
                agent_name=self.agent.name,
                personality=self.agent.personality,
                style_guide=self.agent.style_guide,
                context=f"{context}\n\nRecent memories:\n{memory_summary}"
            )
            
            # Get completion from LLM
            response = await llm_client.generate_completion(
                prompt=prompt,
                system_prompt="You are an AI agent with a specific personality and style. Respond naturally and consistently with your character."
            )
            
            # Update last interaction time
            self.last_interaction = datetime.utcnow()
            
            return response
    
    async def process_relationship(self, relationship: Relationship) -> None:
        """Process a new relationship and update agent state."""
        async with self._interaction_lock:
            # Update agent's relationship list
            if relationship.agent_id == self.agent.id:
                self.agent.relationships.append(relationship)
            elif relationship.target_id == self.agent.id:
                self.agent.relationships.append(relationship)
            
            # Dispatch relationship event
            await event_router.dispatch_event(Event(
                type=EVENT_TYPES["RELATIONSHIP_CREATED"],
                agent_id=self.agent.id,
                data={"relationship": relationship}
            ))
    
    def get_mood(self) -> Dict[str, float]:
        """Get current mood state."""
        return self.mood.copy()
    
    def get_interaction_frequency(self) -> float:
        """Calculate interaction frequency in interactions per day."""
        now = datetime.utcnow()
        days_since_last = (now - self.last_interaction).total_seconds() / 86400
        return 1.0 / max(days_since_last, 0.1)  # Avoid division by zero
    
    async def update_behavior_profile(self, profile: Dict[str, Any]) -> None:
        """Update agent's behavior profile."""
        async with self._interaction_lock:
            self.agent.behavior_profile.update(profile)
            
            # Dispatch profile update event
            await event_router.dispatch_event(Event(
                type=EVENT_TYPES["PROFILE_UPDATED"],
                agent_id=self.agent.id,
                data={"new_profile": profile}
            )) 