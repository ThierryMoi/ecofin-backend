from datetime import datetime
from bson import ObjectId

from model.user_model import UserReadDB ,StatusEnum
from typing import Optional

from datetime import datetime
from pydantic import BaseModel, EmailStr, constr

class UserAuth(UserReadDB):
    access_token : str
    refresh_token: str
    time_refresh_token:int
    time_access_token:int

class LoginUserSchema(BaseModel):
    email: EmailStr
    password: Optional[constr(min_length=4)]
    token: Optional[str]=None





