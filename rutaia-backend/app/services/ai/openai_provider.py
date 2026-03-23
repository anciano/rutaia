# app/services/ai/openai_provider.py

import os
from typing import List, Dict
from openai import OpenAI
from .base import AIProvider

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    async def get_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None, 
        **kwargs
    ) -> str:
        model = model or self.get_default_model()
        # Note: In a real async environment we'd use AsyncOpenAI, 
        # but for this refactor we'll keep the sync call wrapped if needed 
        # or simple client call as per original code.
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content

    def get_default_model(self) -> str:
        return "gpt-4o"
