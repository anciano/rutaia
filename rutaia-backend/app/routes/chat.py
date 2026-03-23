from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.schemas.message import MessageCreate, MessageResponse
from app.models.message import Message
from app.services.ai.factory import ai_service
import uuid

router = APIRouter()

@router.post("/chat", response_model=MessageResponse)
async def chat_endpoint(payload: MessageCreate, db: Session = Depends(get_db)):
    try:
        # Usamos el servicio desacoplado
        answer = await ai_service.chat(payload.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el chat: {str(e)}")
    
    msg = Message(id=str(uuid.uuid4()), content=payload.content, response=answer)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg