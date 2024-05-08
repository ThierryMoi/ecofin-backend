from fastapi import APIRouter, Depends, HTTPException
from typing import List,Union
from model.user_model import UserRead,UserBase,UserUpdate
from configuration.properties import app

from configuration.mongo import USER_COLLECTION
from service.user_service import UserService

from repository.user_repository import UserRepository


user_repository = UserRepository(USER_COLLECTION)
user_service = UserService(user_repository)


router = APIRouter(prefix='/users',tags=['users'])

@router.post("/add", response_model=UserRead)
def create_user(user: UserBase):
    user_id = user_service.create_user(user.dict())
    return {"user_id": user_id, **user.dict()}

@router.get("/get-one", response_model=UserRead)
def get_user(user_id: str):
    user = user_service.get_user_by_id(user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/all", response_model=List[UserRead])
def get_all_users():
    return user_service.get_all_users()

@router.put("/update", response_model=bool)
def update_user(user_id: str, user_update: UserUpdate):
    if user_service.get_user_by_id(user_id):
        return user_service.update_user(user_id, user_update.dict())
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/delete", response_model=bool)
def delete_user(user_id: str):
    if user_service.get_user_by_id(user_id):
        return user_service.delete_user(user_id)
    raise HTTPException(status_code=404, detail="User not found")



app.include_router(router)
