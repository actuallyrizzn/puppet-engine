"""
Core domain models for Puppet Engine.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class MemoryType(str, Enum):
    """Types of memory stored for agents."""
    CORE = "core"
    EVENT = "event"
    INTERACTION = "interaction"
    GENERAL = "general"

class Personality(BaseModel):
    """Agent personality configuration."""
    traits: List[str] = Field(default_factory=list)
    values: List[str] = Field(default_factory=list)
    speaking_style: Optional[str] = Field(default=None, max_length=50)
    interests: List[str] = Field(default_factory=list)

    @validator('traits', 'values', 'interests', pre=True, each_item=True)
    def validate_list_items(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class Agent(BaseModel):
    """Agent configuration and state."""
    id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    personality: Personality = Field(default_factory=Personality)
    custom_system_prompt: Optional[str] = Field(default=None, max_length=500)
    rotating_system_prompts: List[str] = Field(default_factory=list)
    behavior: Dict[str, Any] = Field(default_factory=dict)
    current_mood: Dict[str, float] = Field(default_factory=dict)
    last_post_time: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MemoryItem(BaseModel):
    """Individual memory item for agents."""
    id: Optional[str] = None
    agent_id: str
    type: MemoryType
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    importance: float = Field(default=1.0, ge=0.0, le=10.0)
    vector_embedding: Optional[List[float]] = None

class Event(BaseModel):
    """Event model for the event engine."""
    id: Optional[str] = None
    type: str
    agent_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 1  # 0=low, 1=normal, 2=high, 3=critical
    scheduled_for: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

class Tweet(BaseModel):
    """Twitter/X tweet model."""
    id: Optional[str] = None
    text: str = Field(..., max_length=280)
    agent_id: str
    reply_to: Optional[str] = None
    media_urls: List[str] = Field(default_factory=list)
    posted_at: Optional[datetime] = None
    twitter_id: Optional[str] = None
    engagement_metrics: Dict[str, int] = Field(default_factory=dict)

class LLMResponse(BaseModel):
    """Response from LLM providers."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow) 