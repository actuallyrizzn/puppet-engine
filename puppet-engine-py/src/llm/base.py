from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = {}

class BaseLLMProvider(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get("model", "gpt-4")
        self.max_tokens = config.get("max_tokens", 1024)
        self.temperature = config.get("temperature", 0.7)
        self.rate_limit_delay = config.get("rate_limit_delay", 1.0)

    @abstractmethod
    async def generate_content(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> LLMResponse:
        pass

    @abstractmethod
    async def generate_tweet(self, agent, prompt: str = "") -> str:
        pass 