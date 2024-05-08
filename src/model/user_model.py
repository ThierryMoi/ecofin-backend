
from pydantic import BaseModel,EmailStr,Field
from typing import Optional,List
from enum import Enum
from datetime import datetime
from bson import ObjectId

class UserBase(BaseModel):
    _id: ObjectId
    nom_prenom: Optional[str]
    email: Optional[str]

    class Config:
        allow_population_by_field_name = True


class UserRead(UserBase):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]


class UserUpdate(UserBase):
    updated_at: datetime

class UserUpdate(UserBase):
    deleted_at: datetime


