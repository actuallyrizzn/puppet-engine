from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

@dataclass
class Personality:
    name: str
    description: str
    traits: List[str]

@dataclass
class StyleGuide:
    tone: str
    language: str
    quirks: Optional[List[str]] = None

@dataclass
class MemoryItem:
    id: int
    agent_id: int
    content: str
    timestamp: str

@dataclass
class Relationship:
    agent_id: int
    target_id: int
    relationship_type: str
    strength: float

class Event(BaseModel):
    """Event model."""
    type: str
    agent_id: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None

class Agent(BaseModel):
    """Agent model."""
    id: str
    name: str
    description: str
    personality: str
    mood: str
    created_at: str
    twitter_credentials: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None

class Memory(BaseModel):
    """Memory model."""
    id: Optional[str] = None
    agent_id: str
    content: str
    type: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

class Relationship(BaseModel):
    """Relationship model."""
    id: Optional[str] = None
    agent1_id: str
    agent2_id: str
    type: str
    strength: float
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None 