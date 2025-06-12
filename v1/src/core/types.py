from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

@dataclass
class Personality:
    traits: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    speaking_style: str = ""
    interests: List[str] = field(default_factory=list)

@dataclass
class StyleGuide:
    voice: str = ""
    tone: str = ""
    formatting: Dict[str, Any] = field(default_factory=lambda: {
        "usesHashtags": False,
        "hashtagStyle": "",
        "usesEmojis": False,
        "emojiFrequency": "",
        "capitalization": "",
        "sentenceLength": ""
    })
    topics_to_avoid: List[str] = field(default_factory=list)

@dataclass
class Relationship:
    target_agent_id: str
    sentiment: float = 0.0  # -1.0 to 1.0
    familiarity: float = 0.0  # 0.0 to 1.0
    trust: float = 0.0  # 0.0 to 1.0
    last_interaction_date: Optional[datetime] = None
    recent_interactions: List[Any] = field(default_factory=list)
    shared_experiences: List[Any] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

@dataclass
class MemoryItem:
    content: str
    type: str = "general"  # 'core', 'interaction', 'event', 'general'
    id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    importance: float = 0.5  # 0.0 to 1.0
    emotional_valence: float = 0.0  # -1.0 to 1.0
    associations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentMemory:
    core_memories: List[MemoryItem] = field(default_factory=list)
    recent_events: List[Any] = field(default_factory=list)
    recent_posts: List[Any] = field(default_factory=list)
    relationships: Dict[str, Relationship] = field(default_factory=dict)
    long_term_memories: List[MemoryItem] = field(default_factory=list)

    def add_memory(self, content: str, type: str = "general", importance: float = 0.5) -> MemoryItem:
        memory = MemoryItem(content=content, type=type, importance=importance)
        if type == "core":
            self.core_memories.append(memory)
        else:
            self.long_term_memories.append(memory)
        return memory

    def get_relationship(self, target_agent_id: str) -> Relationship:
        if target_agent_id not in self.relationships:
            self.relationships[target_agent_id] = Relationship(target_agent_id=target_agent_id)
        return self.relationships[target_agent_id]

@dataclass
class Tweet:
    id: str = ""
    content: str = ""
    media_urls: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    author_id: str = ""
    reply_to_id: Optional[str] = None
    quote_tweet_id: Optional[str] = None
    is_thread: bool = False
    thread_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Agent:
    id: str = ""
    name: str = ""
    description: str = ""
    personality: Personality = field(default_factory=Personality)
    style_guide: StyleGuide = field(default_factory=StyleGuide)
    memory: AgentMemory = field(default_factory=AgentMemory)
    custom_system_prompt: Optional[str] = None
    rotating_system_prompts: List[str] = field(default_factory=list)
    behavior: Dict[str, Any] = field(default_factory=lambda: {
        "postFrequency": {
            "minHoursBetweenPosts": 3,
            "maxHoursBetweenPosts": 12,
            "peakPostingHours": []
        },
        "interactionPatterns": {
            "replyProbability": 0.5,
            "quoteTweetProbability": 0.3,
            "likeProbability": 0.7
        },
        "contentPreferences": {
            "maxThreadLength": 3,
            "typicalPostLength": 240,
            "linkSharingFrequency": 0.2
        }
    })
    current_mood: Dict[str, float] = field(default_factory=lambda: {
        "valence": 0.0,
        "arousal": 0.0,
        "dominance": 0.5
    })
    goals: List[str] = field(default_factory=list)
    last_post_time: Optional[datetime] = None

    def update_mood(self, valence_shift: float, arousal_shift: float, dominance_shift: float):
        self.current_mood["valence"] = max(-1.0, min(1.0, self.current_mood["valence"] + valence_shift))
        self.current_mood["arousal"] = max(0.0, min(1.0, self.current_mood["arousal"] + arousal_shift))
        self.current_mood["dominance"] = max(0.0, min(1.0, self.current_mood["dominance"] + dominance_shift))

@dataclass
class Event:
    id: str = ""
    type: str = ""  # 'news', 'interaction', 'mood_shift', 'scheduled', 'random'
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    target_agent_ids: List[str] = field(default_factory=list)  # empty means broadcast
    priority: str = "normal"  # 'low', 'normal', 'high', 'critical' 