from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from ..config import settings
from ..events.router import event_router
from ..events.handlers import EVENT_TYPES

class LLMClient:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = "gpt-4-turbo-preview"  # Default model
        self._max_retries = 3
        self._base_delay = 1  # Base delay in seconds
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError))
    )
    async def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        model: Optional[str] = None
    ) -> str:
        """Generate a completion using the LLM."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=model or self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Dispatch error event
            await event_router.dispatch_event(Event(
                id=0,
                type=EVENT_TYPES["ERROR_OCCURRED"],
                payload={
                    "error_type": "llm_error",
                    "error_message": str(e)
                },
                timestamp=datetime.utcnow().isoformat()
            ))
            raise
    
    async def generate_agent_prompt(
        self,
        agent_name: str,
        personality: Dict[str, Any],
        style_guide: Dict[str, Any],
        context: Optional[str] = None
    ) -> str:
        """Generate a system prompt for an agent."""
        base_prompt = f"""You are {agent_name}, an AI agent with the following personality:
        
Personality: {personality['name']}
Description: {personality['description']}
Traits: {', '.join(personality['traits'])}

Style Guide:
Tone: {style_guide['tone']}
Language: {style_guide['language']}
Quirks: {', '.join(style_guide.get('quirks', []))}

"""
        
        if context:
            base_prompt += f"\nContext: {context}\n"
        
        base_prompt += """
Your responses should reflect your personality and style guide. Be consistent in your character and maintain the specified tone and language patterns."""
        
        return base_prompt
    
    async def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze the sentiment of text to help determine mood."""
        prompt = f"""Analyze the sentiment of the following text and provide scores for:
1. Positivity (0-1)
2. Energy (0-1)
3. Formality (0-1)

Text: {text}

Provide the scores in a simple format like:
positivity: 0.8
energy: 0.6
formality: 0.3
"""
        
        response = await self.generate_completion(
            prompt=prompt,
            temperature=0.3,
            max_tokens=100
        )
        
        # Parse the response
        scores = {}
        for line in response.split('\n'):
            if ':' in line:
                key, value = line.split(':')
                try:
                    scores[key.strip()] = float(value.strip())
                except ValueError:
                    continue
        
        return scores
    
    async def generate_memory_summary(self, memories: List[Dict[str, Any]]) -> str:
        """Generate a summary of recent memories."""
        if not memories:
            return "No recent memories to summarize."
        
        memory_text = "\n".join([
            f"- {m['content']} ({m['timestamp']})"
            for m in memories
        ])
        
        prompt = f"""Summarize the following memories in a concise way that captures the key events and their significance:

{memory_text}

Provide a brief summary that captures the main themes and important events."""
        
        return await self.generate_completion(
            prompt=prompt,
            temperature=0.5,
            max_tokens=200
        )

# Global LLM client instance
llm_client = LLMClient() 