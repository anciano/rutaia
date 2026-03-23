# app/schemas/ia.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SuggestionImpact(BaseModel):
    tiempo: str = Field(..., description="Impacto en tiempo, e.g. '+2 horas', '-30 min'")
    presupuesto: float = Field(..., description="Impacto en presupuesto en CLP")

class SuggestionItem(BaseModel):
    id: str
    tipo: str = Field(..., description="Tipo de sugerencia: agregar, mover, reemplazar, eliminar")
    titulo: str
    descripcion: str
    justificacion: str
    impacto: SuggestionImpact
    action_data: Optional[Dict[str, Any]] = Field(None, description="Metadata técnica para ejecutar la acción (item_id, catalog_item_id, etc.)")

class ItineraryItemInput(BaseModel):
    id: Optional[str] = None
    nombre: str
    duracion: int
    precio: float

class ItineraryDayInput(BaseModel):
    dia: int
    items: List[ItineraryItemInput]

class SuggestionRequest(BaseModel):
    ciudad_inicio: str
    dias: int
    presupuesto: float
    num_personas: int = Field(2, description="Número de personas en el viaje")
    preferencias: List[str]
    itinerario: List[ItineraryDayInput]
    wishlist: List[ItineraryItemInput] = Field(default_factory=list, description="Ítems en la bolsa de intereses (pendientes)")

class SuggestionResponse(BaseModel):
    sugerencias: List[SuggestionItem]
