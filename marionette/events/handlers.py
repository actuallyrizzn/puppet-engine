from typing import Dict, Any, Optional
from datetime import datetime
from ..types import Event, Agent
from ..agents.manager import agent_manager
from ..memory.database import db
from .router import event_router

# Event Types
EVENT_TYPES = {
    "AGENT_CREATED": "agent.created",
    "AGENT_UPDATED": "agent.updated",
    "MEMORY_CREATED": "memory.created",
    "RELATIONSHIP_CREATED": "relationship.created",
    "MOOD_CHANGED": "mood.changed",
    "INTERACTION_STARTED": "interaction.started",
    "INTERACTION_COMPLETED": "interaction.completed",
    "ERROR_OCCURRED": "error.occurred"
}

async def handle_agent_created(event: Event):
    """Handle agent creation events."""
    agent_id = event.payload["agent_id"]
    agent = await agent_manager.get_agent(agent_id)
    if agent:
        # Log the creation
        await db.add_memory(
            agent_id=agent_id,
            content=f"Agent {agent.name} was created with personality {agent.personality.name}"
        )

async def handle_memory_created(event: Event):
    """Handle memory creation events."""
    agent_id = event.payload["agent_id"]
    content = event.payload["content"]
    
    # Update agent's mood based on memory content if needed
    # TODO: Implement mood analysis
    pass

async def handle_relationship_created(event: Event):
    """Handle relationship creation events."""
    agent_id = event.payload["agent_id"]
    target_id = event.payload["target_id"]
    relationship_type = event.payload["relationship_type"]
    
    agent = await agent_manager.get_agent(agent_id)
    target = await agent_manager.get_agent(target_id)
    
    if agent and target:
        await db.add_memory(
            agent_id=agent_id,
            content=f"Created {relationship_type} relationship with {target.name}"
        )

async def handle_mood_changed(event: Event):
    """Handle mood change events."""
    agent_id = event.payload["agent_id"]
    old_mood = event.payload.get("old_mood")
    new_mood = event.payload["new_mood"]
    
    agent = await agent_manager.get_agent(agent_id)
    if agent:
        await db.add_memory(
            agent_id=agent_id,
            content=f"Mood changed from {old_mood} to {new_mood}"
        )

async def handle_error(event: Event):
    """Handle error events."""
    error_type = event.payload["error_type"]
    error_message = event.payload["error_message"]
    agent_id = event.payload.get("agent_id")
    
    if agent_id:
        await db.add_memory(
            agent_id=agent_id,
            content=f"Error occurred: {error_type} - {error_message}"
        )

def register_default_handlers():
    """Register all default event handlers."""
    event_router.register_handler(EVENT_TYPES["AGENT_CREATED"], handle_agent_created)
    event_router.register_handler(EVENT_TYPES["MEMORY_CREATED"], handle_memory_created)
    event_router.register_handler(EVENT_TYPES["RELATIONSHIP_CREATED"], handle_relationship_created)
    event_router.register_handler(EVENT_TYPES["MOOD_CHANGED"], handle_mood_changed)
    event_router.register_handler(EVENT_TYPES["ERROR_OCCURRED"], handle_error)

# Register handlers when module is imported
register_default_handlers() 