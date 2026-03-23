# app/services/ai/base.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AIProvider(ABC):
    @abstractmethod
    async def get_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        **kwargs
    ) -> str:
        """Generates a chat completion based on the messages provided."""
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        """Returns the default model name for this provider."""
        pass
