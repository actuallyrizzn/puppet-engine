from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from .types import Agent, Memory, Relationship, Event
from .memory.database import Database
from .agents.manager import AgentManager
from .events.router import event_router, EVENT_TYPES
from .twitter.client import TwitterClient
from .config.settings import settings

app = FastAPI(title="Puppet Engine API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = Database()
agent_manager = AgentManager(db)
twitter_client = TwitterClient(
    credentials=settings.twitter_credentials,
    bearer_token=settings.twitter_bearer_token
)

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    await db.initialize()
    await event_router.start()
    
    # Register Twitter clients for existing agents
    for agent in await agent_manager.list_agents():
        if agent.twitter_credentials:
            twitter_client.register_agent_client(agent.id, agent.twitter_credentials)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await event_router.stop()
    await db.close()

# Agent endpoints
@app.post("/agents", response_model=Agent)
async def create_agent(agent: Agent):
    """Create a new agent."""
    created_agent = await agent_manager.create_agent(agent)
    
    # Register Twitter client if credentials provided
    if agent.twitter_credentials:
        twitter_client.register_agent_client(agent.id, agent.twitter_credentials)
    
    # Dispatch agent created event
    await event_router.dispatch_event(Event(
        type=EVENT_TYPES["AGENT_CREATED"],
        agent_id=agent.id,
        data={
            "agent": created_agent.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
    ))
    
    return created_agent

@app.get("/agents", response_model=List[Agent])
async def list_agents():
    """List all agents."""
    return await agent_manager.list_agents()

@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get an agent by ID."""
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

# Memory endpoints
@app.post("/agents/{agent_id}/memories", response_model=Memory)
async def add_memory(agent_id: str, memory: Memory):
    """Add a memory for an agent."""
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    created_memory = await agent_manager.add_memory(agent_id, memory)
    
    # Dispatch memory created event
    await event_router.dispatch_event(Event(
        type=EVENT_TYPES["MEMORY_CREATED"],
        agent_id=agent_id,
        data={
            "memory": created_memory.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
    ))
    
    return created_memory

@app.get("/agents/{agent_id}/memories", response_model=List[Memory])
async def list_memories(agent_id: str):
    """List memories for an agent."""
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return await agent_manager.list_memories(agent_id)

# Relationship endpoints
@app.post("/relationships", response_model=Relationship)
async def add_relationship(relationship: Relationship):
    """Add a relationship between agents."""
    # Verify both agents exist
    agent1 = await agent_manager.get_agent(relationship.agent1_id)
    agent2 = await agent_manager.get_agent(relationship.agent2_id)
    if not agent1 or not agent2:
        raise HTTPException(status_code=404, detail="One or both agents not found")
    
    created_relationship = await agent_manager.add_relationship(relationship)
    
    # Dispatch relationship created event
    await event_router.dispatch_event(Event(
        type=EVENT_TYPES["RELATIONSHIP_CREATED"],
        agent_id=relationship.agent1_id,
        data={
            "relationship": created_relationship.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
    ))
    
    return created_relationship

@app.get("/relationships", response_model=List[Relationship])
async def list_relationships():
    """List all relationships."""
    return await agent_manager.list_relationships()

# Twitter endpoints
@app.post("/agents/{agent_id}/tweets")
async def post_tweet(agent_id: str, content: str, options: Optional[Dict[str, Any]] = None):
    """Post a tweet from an agent."""
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        result = await twitter_client.post_tweet(agent, content, options)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/{agent_id}/stream")
async def start_mention_stream(agent_id: str):
    """Start streaming mentions for an agent."""
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    async def on_mention(tweet):
        # Create memory from mention
        memory = Memory(
            agent_id=agent_id,
            content=f"Received mention: {tweet.text}",
            type="mention",
            metadata={
                "tweet_id": tweet.id,
                "author_id": tweet.author_id,
                "created_at": tweet.created_at.isoformat()
            }
        )
        await agent_manager.add_memory(agent_id, memory)
    
    try:
        result = await twitter_client.start_mention_stream(agent, on_mention)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/agents/{agent_id}/stream")
async def stop_mention_stream(agent_id: str):
    """Stop streaming mentions for an agent."""
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    twitter_client.stop_mention_stream(agent_id)
    return {"status": "stream stopped"}

@app.get("/agents/{agent_id}/timeline/{user_id}")
async def get_user_timeline(agent_id: str, user_id: str, options: Optional[Dict[str, Any]] = None):
    """Get recent tweets from a user's timeline."""
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        result = await twitter_client.get_user_timeline(agent, user_id, options)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Event endpoints
@app.get("/events", response_model=List[Event])
async def list_events():
    """List recent events."""
    # TODO: Implement event storage and retrieval
    return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
