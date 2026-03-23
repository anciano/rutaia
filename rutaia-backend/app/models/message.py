from sqlalchemy import Column, String
from app.models.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    content = Column(String)
    response = Column(String)