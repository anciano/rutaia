# app/services/openai_service.py
from openai import OpenAI
from app.settings import OPENAI_API_KEY

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_json(self, prompt: str, system_prompt: str, model="gpt-4o-mini") -> str:
        """Calls OpenAI with a system prompt and returns a JSON string."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in OpenAIService: {e}")
            raise e

openai_service = OpenAIService()
