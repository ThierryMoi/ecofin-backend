from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
from configuration.posgres import engine
Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    message_id = Column(String, primary_key=True)
    discussion_id = Column(String)
    question = Column(String)
    reponse = Column(String, unique=True)
    appreciation = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)

class MessageResponse(BaseModel):
    message_id: str
    discussion_id: str
    question: str
    response: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime
    
Base.metadata.create_all(engine)
