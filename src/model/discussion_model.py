
from pydantic import BaseModel,EmailStr,Field
from typing import Optional,List
from enum import Enum
from datetime import datetime
from bson import ObjectId

class DiscussionBase(BaseModel):
    user_id: Optional[str]

class DiscussionRead(DiscussionBase):
    name: Optional[str]
    discussion_id:str 
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]



class DiscussionReadPaginer(BaseModel):
    discussions: Optional[List[DiscussionRead]]
    page_size:int
    page:int
    nb_pages: Optional[int]


class DiscussionUpdate(BaseModel):
    name: Optional[str]


class DiscussionDelete(DiscussionBase):
    deleted_at: datetime


