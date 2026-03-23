# app/routes/ia.py
from fastapi import APIRouter, HTTPException
from app.schemas.ia import SuggestionRequest, SuggestionResponse
from app.services.ai_service import ai_service

router = APIRouter(prefix="/ia", tags=["IA"])

@router.post("/sugerencias", response_model=SuggestionResponse)
async def get_ia_suggestions(request: SuggestionRequest):
    """
    Recibe un itinerario y devuelve sugerencias de mejora generadas por IA.
    """
    try:
        suggestions = ai_service.generate_suggestions(request)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
