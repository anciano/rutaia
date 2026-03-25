from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    nombre: str
    correo: str
    role: str

class UserResponse(UserBase):
    id: str
    provider: Optional[str] = None
    creado_en: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserUpdateRole(BaseModel):
    role: str
