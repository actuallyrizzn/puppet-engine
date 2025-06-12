import os
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

class OpenAIClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def chat(self, messages, model="gpt-3.5-turbo"):
        resp = await openai.ChatCompletion.acreate(
            model=model,
            messages=messages
        )
        return resp["choices"][0]["message"]["content"] 