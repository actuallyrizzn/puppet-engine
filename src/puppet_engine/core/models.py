seline Integration Tests for Puppet Engine Migration

This test suite captures the current Node.js behavior to ensure
the Python migration maintains functional parity.

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class MemoryType(str, Enum):
    CORE = core    EVENT =event"
    INTERACTION =interaction"
    GENERAL =general
class Personality(BaseModel):
    traits: List[str] = Field(default_factory=list, max_items=20)
    values: List[str] = Field(default_factory=list, max_items=10)
    speaking_style: str = Field(max_length=50   interests: List[str] = Field(default_factory=list, max_items=15)
    
    @validator('traits', 'values', 'interests')
    def validate_list_items(cls, v):
        return [item.strip() for item in v if item.strip()]


class Agent(BaseModel):
    id: str = Field(regex=r^[a-z0 name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=1000)
    personality: Personality = Field(default_factory=Personality)
    custom_system_prompt: Optional[str] = Field(max_length=500   rotating_system_prompts: List[str] = Field(default_factory=list)
    behavior: Dict[str, Any] = Field(default_factory=dict)
    current_mood: Dict[str, float] = Field(default_factory=dict)
    last_post_time: Optional[datetime] = None
    goals: List[str] = Field(default_factory=list)
    style_guide: Optional[str] = Field(max_length=100

class MemoryItem(BaseModel):
    id: str
    agent_id: str
    type: MemoryType
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    importance: float = Field(default=1.0e=0.0, le=10

class Event(BaseModel):
    id: str
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    priority: int = Field(default=1, ge=1, le=10   processed: bool =false
class LLMResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dictstr, int]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Tweet(BaseModel):
    id: str
    text: str
    author_id: str
    created_at: datetime
    reply_to: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


class HealthStatus(BaseModel):
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    uptime: float
    services: Dict[str, str] = Field(default_factory=dict) 