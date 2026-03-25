from pydantic import BaseModel
from typing import Optional

class MessageCreate(BaseModel):
    content: str
    user_id: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    content: str
    response: str