from pydantic import BaseModel,EmailStr
from typing import Optional,List
from enum import Enum
from datetime import datetime
from bson import ObjectId


class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    banned = "banned"

class ConnectionType(str, Enum):
    simple = "simple"
    social_media = "social_media"

    
class RoleEnum(str, Enum):
    simple = "simple"
    admin_system = "admin_system"

class UserBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    role: List[RoleEnum] = [RoleEnum.simple] 
     

    





class UserUpdate(BaseModel):
    nom: Optional[str] 
    prenom: Optional[str] 
    username: Optional[str]



class UserUpdateInBD(BaseModel):
    nom: Optional[str] 
    prenom: Optional[str] 
    username: Optional[str]
    status: Optional[str]
    updated_at: Optional[datetime]


class UserReadSimple(UserBase):
    id_user: Optional[str]  
    status: Optional[StatusEnum]
    hashed_password: Optional[str]
    username: Optional[str]
    created_at: Optional[datetime]

    #deleted_at: Optional[datetime]
    updated_at: Optional[datetime]

class UserReadDB(UserBase):
    id_user: Optional[str]  
    status: StatusEnum
   
    created_at: Optional[datetime]
 
    username: Optional[str]

    updated_at: Optional[datetime]


    
class UserCreate(UserBase):
    password: Optional[str]
    confirm_password: Optional[str] 

    
class UserInDB(UserBase):
    _id: Optional[str] 
    hashed_password: str
    username: Optional[str]
    status: Optional[StatusEnum]= StatusEnum.inactive
    supprime: Optional[bool ]= False
    created_at: Optional[datetime]
    deleted_at: Optional[datetime]
    updated_at: Optional[datetime]

class OtpModel(BaseModel):
    email: str
    code: str
    secretkey:str
    date_creation: Optional[datetime]


class UserMdp(BaseModel):
    old_password:str
    new_password:str
    confirm_password:str
    
class PasswordResetRequest(BaseModel):
    email: str
    
class PasswordResetToken(BaseModel):
    token: str
