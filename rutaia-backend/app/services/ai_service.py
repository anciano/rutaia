# app/services/ai_service.py
import json
from typing import List
from app.schemas.ia import SuggestionRequest, SuggestionResponse, SuggestionItem
from app.services.openai_service import openai_service

class AIService:
    def generate_suggestions(self, request: SuggestionRequest) -> SuggestionResponse:
        system_prompt = """
        Eres un asistente experto en planificación de viajes por la Patagonia chilena (Carretera Austral).
        Tu objetivo es analizar el itinerario del usuario y proponer exactamente 3 a 5 mejoras estratégicas.
        
        Reglas de Negocio:
        1. Tipos permitidos: 'agregar', 'mover', 'reemplazar', 'eliminar'.
        2. Mantente dentro o cerca del presupuesto total: {presupuesto} CLP.
        3. Respeta las preferencias: {preferencias}.
        4. Considera que el grupo es de {num_personas} personas.
        5. Sé específico con lugares reales de la región.
        6. Devuelve un objeto JSON con la clave 'sugerencias'.
        
        AFINIDAD Y WISHLIST:
        Se te proporciona una 'wishlist' con lugares que el usuario ya marcó como afines en pasos anteriores.
        Si vas a sugerir 'agregar' algo, PRIORIZA elementos de esta wishlist que encajen lógicamente.
        
        IMPORTANTE: Cada sugerencia DEBE incluir un campo 'action_data' con la siguiente estructura según el tipo:
        - Si tipo es 'agregar': {{"nombre": "...", "descripcion": "...", "dia": N, "precio": X, "duracion": Y}}
        - Si tipo es 'eliminar': {{"item_id": "UUID_DEL_ITEM"}}
        - Si tipo es 'reemplazar': {{"item_id_to_remove": "UUID", "new_item": {{"nombre": "...", "dia": N, ...}}}}
        - Si tipo es 'mover': {{"item_id": "UUID", "new_day": N}}
        
        Formato de salida JSON esperado:
        {{
          "sugerencias": [
            {{
              "id": "sug_1",
              "tipo": "...",
              "titulo": "...",
              "descripcion": "...",
              "justificacion": "...",
              "impacto": {{"tiempo": "...", "presupuesto": 0}},
              "action_data": {{ ... }}
            }}
          ]
        }}
        """.format(presupuesto=request.presupuesto, preferencias=", ".join(request.preferencias), num_personas=request.num_personas)

        # Serializar el itinerario y wishlist
        itinerario_str = json.dumps([day.dict() for day in request.itinerario], indent=2)
        wishlist_str = json.dumps([item.dict() for item in request.wishlist], indent=2)
        
        user_prompt = f"""
        Ciudad de inicio: {request.ciudad_inicio}
        Días totales: {request.dias}
        Pasajeros: {request.num_personas}
        Presupuesto: {request.presupuesto} CLP
        Preferencias: {", ".join(request.preferencias)}
        
        Itinerario actual:
        {itinerario_str}
        
        Bolsa de Intereses (Marcados como afines por el usuario):
        {wishlist_str}
        
        Genera sugerencias de mejora personalizadas.
        """

        response_str = openai_service.generate_json(user_prompt, system_prompt)
        
        try:
            data = json.loads(response_str)
            return SuggestionResponse(**data)
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            # Fallback a un objeto vacío o error manejado
            return SuggestionResponse(sugerencias=[])

ai_service = AIService()
