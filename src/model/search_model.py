from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Content(BaseModel):
    numeros_paragraphe: str = Field(..., alias="Numeros_paragraphe")
    date_parution: datetime = Field(..., alias="Dateparution")
    titre: str = Field(..., alias="Titre")
    description: str = Field(..., alias="Description")

class Rapport(BaseModel):
    base_de_donnee: str
    partition: str
    score: float
    content: Content

class RapportList(BaseModel):
    rapports: List[Rapport]
