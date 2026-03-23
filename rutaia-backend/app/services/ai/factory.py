# app/services/ai/factory.py

import os
from .openai_provider import OpenAIProvider
# Import other providers here as they are implemented

def get_ai_provider():
    provider_name = os.getenv("AI_PROVIDER", "openai").lower()
    
    if provider_name == "openai":
        return OpenAIProvider()
    # elif provider_name == "gemini":
    #     return GeminiProvider()
    else:
        # Fallback to OpenAI for now
        return OpenAIProvider()

class AIService:
    def __init__(self, provider=None):
        self.provider = provider or get_ai_provider()
        self.system_prompts = {
            "default": "Eres un asesor inteligente y amigable que responde preguntas sobre turismo, actividades, cultura y vida regional.",
            "planner": "Eres un planificador experto en itinerarios regionales. Tu objetivo es optimizar el viaje del usuario."
        }

    async def chat(self, user_content: str, role: str = "default") -> str:
        system_content = self.system_prompts.get(role, self.system_prompts["default"])
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
        return await self.provider.get_chat_completion(messages)

# Global instances
ai_service = AIService()
