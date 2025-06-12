from dataclasses import dataclass, field
from typing import Optional, List
from marionette.types import Personality, StyleGuide, Relationship, MemoryItem

@dataclass
class Agent:
    id: int
    name: str
    personality: Personality
    style_guide: StyleGuide
    mood: Optional[str] = None  # VAD mood tracking (Valence-Arousal-Dominance)
    relationships: List[Relationship] = field(default_factory=list)
    behavior_profile: dict = field(default_factory=dict)
    memories: List[MemoryItem] = field(default_factory=list)

    def update_mood(self, vad: tuple):
        # Simple VAD mood tracking (valence, arousal, dominance)
        self.mood = f"V:{vad[0]:.2f} A:{vad[1]:.2f} D:{vad[2]:.2f}"

    def add_memory(self, memory: MemoryItem):
        self.memories.append(memory)

    def add_relationship(self, rel: Relationship):
        self.relationships.append(rel)

    def system_prompt(self) -> str:
        # Stub: generate a system prompt for LLM
        return f"Agent {self.name} with personality {self.personality.name} and style {self.style_guide.tone}" 