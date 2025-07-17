from .base import BaseLLMProvider, LLMResponse
from typing import Dict, Any, Optional

class FakeLLMProvider(BaseLLMProvider):
    async def generate_content(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> LLMResponse:
        return LLMResponse(
            content=f"[FAKE LLM] {prompt}",
            model=self.model,
            usage={"prompt_tokens": len(prompt.split()), "completion_tokens": 5},
            metadata={"provider": "fake"}
        )

    async def generate_tweet(self, agent, prompt: str = "") -> str:
        return f"[FAKE TWEET for {getattr(agent, 'name', 'agent')}] {prompt}" 