

from pydantic import BaseModel,EmailStr,Field
from typing import Optional,List
from enum import Enum
from datetime import datetime
from bson import ObjectId




class MessageBase(BaseModel):
    discussion_id: str
    question: str
    response: str
    user_id: str





class MessageRead(MessageBase):
    message_id: str 
    appreciation: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]


class MessageReadPaginer(BaseModel):
    message: Optional[List[MessageRead]]
    page_size:int
    page:int
    nb_pages: Optional[int]


class MessageResponse(MessageBase):
    message_id: str
    response: str
    created_at: Optional[datetime]
    