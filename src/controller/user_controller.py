from fastapi import APIRouter, Depends, HTTPException
from typing import List,Union
from model.user_model import User,UserResponse
from configuration.properties import app

from configuration.posgres import CONNECTION_STRING



from service.user_service import UserService
from repository.user_repository import UserRepository


user_repository = UserRepository(CONNECTION_STRING)
user_service = UserService(user_repository)

router = APIRouter()


@router.post("/users/", response_model=Union[dict,None])
def create_user(user: UserResponse):
    created_user = user_service.create_user(user.dict())
    return created_user

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: str):
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

@router.get("/users/", response_model=List[UserResponse])
def get_all_users():
    return user_service.get_all_users()

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user( user_id: str, user: UserResponse):
    updated_user = user_service.update_user(user_id, user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return updated_user

@router.delete("/users/{user_id}")
def delete_user(user_id: str):
    deleted_user = user_service.delete_user(user_id)
    if deleted_user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"message": "Utilisateur supprimé avec succès"}

app.include_router(router)
