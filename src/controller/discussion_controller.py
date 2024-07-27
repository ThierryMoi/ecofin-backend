from fastapi import APIRouter, Depends, HTTPException
from typing import List, Union
from model.discussion_model import (
    DiscussionRead,
    DiscussionBase,
    DiscussionUpdate,
    DiscussionReadPaginer
)
from configuration.properties import app
from configuration.mongo import DISCUSSION_COLLECTION
from service.discussion_service import DiscussionService
from repository.discussion_repository import DiscussionRepository
from service.auth_service import AuthJWT, require_user


discussion_repository = DiscussionRepository(DISCUSSION_COLLECTION)
discussion_service = DiscussionService(discussion_repository)

router = APIRouter(prefix='/discussions', tags=['discussions'])

@router.post("/add", response_model=dict)
def create_discussion(discussion: DiscussionBase , Authorize: AuthJWT = Depends()):
    
    Authorize.jwt_required()
    #user_id = Authorize.get_jwt_subject()
        
    discussion_id = discussion_service.create_discussion(discussion.dict())
    return {"discussion_id": discussion_id}

@router.get("/get-one", response_model=DiscussionRead)
def get_discussion(discussion_id: str, Authorize: AuthJWT = Depends()):
    
    Authorize.jwt_required()
    #user_id = Authorize.get_jwt_subject()
    discussion = discussion_service.get_discussion_by_id(discussion_id)
    print(discussion)
    if discussion:
        return discussion
    raise HTTPException(status_code=404, detail="Discussion not found")

@router.get("/all", response_model=DiscussionReadPaginer)
def get_all_discussions(page: int, page_size: int, Authorize: AuthJWT = Depends()):
    
    Authorize.jwt_required()
    #user_id = Authorize.get_jwt_subject()
    return discussion_service.get_all_discussions(page, page_size)


@router.get("/all-by-user", response_model=DiscussionReadPaginer)
def get_all_discussions_by_user_controller(page: int, page_size: int, user_id: str, Authorize: AuthJWT = Depends()):
    
    Authorize.jwt_required()
    #user_id = Authorize.get_jwt_subject()
    return discussion_service.get_all_discussions_by_user(user_id, page, page_size)

@router.put("/update", response_model=bool)
def update_discussion(discussion_id: str, discussion_update: DiscussionUpdate, Authorize: AuthJWT = Depends()):
    
    Authorize.jwt_required()
    #user_id = Authorize.get_jwt_subject()
    if discussion_service.get_discussion_by_id(discussion_id):
        return discussion_service.update_discussion(discussion_id, discussion_update.dict())
    raise HTTPException(status_code=404, detail="Discussion not found")

@router.delete("/delete", response_model=bool)
def delete_discussion(discussion_id: str, Authorize: AuthJWT = Depends()):
    
    Authorize.jwt_required()
    #user_id = Authorize.get_jwt_subject()
    if discussion_service.get_discussion_by_id(discussion_id):
        return discussion_service.delete_discussion(discussion_id)
    raise HTTPException(status_code=404, detail="Discussion not found")

app.include_router(router)
