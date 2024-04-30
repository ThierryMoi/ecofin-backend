from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
from configuration.posgres import engine
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(String, primary_key=True)
    nom_prenom = Column(String)
    email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)

class UserResponse(BaseModel):
    user_id: str
    nom_prenom: str
    email: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime
    
Base.metadata.create_all(engine)
