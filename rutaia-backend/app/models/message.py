from sqlalchemy import Column, String, ForeignKey
from app.models.database import Base

class Message(Base):
    __tablename__ = "messages"

    id       = Column(String, primary_key=True, index=True)
    user_id  = Column(String, ForeignKey("users.id"), nullable=True) # Asociamos con el usuario
    content  = Column(String)
    response = Column(String)