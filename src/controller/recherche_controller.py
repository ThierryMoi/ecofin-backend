from fastapi import APIRouter, HTTPException,Depends
from datetime import datetime
from configuration.properties import app
from service.auth_service import AuthJWT
import tiktoken
from configuration.openai import CLIENT_OPENAI

from configuration.mongo import MESSAGE_COLLECTION,DISCUSSION_COLLECTION
from service.message_service import MessageService
from model.search_model import RapportList
from repository.message_repository import MessageRepository



from service.discussion_service import DiscussionService
from repository.discussion_repository import DiscussionRepository

discussion_repository = DiscussionRepository(DISCUSSION_COLLECTION)


message_repository = MessageRepository(MESSAGE_COLLECTION)
message_service = MessageService(message_repository,discussion_repository)
router = APIRouter(prefix='/similarity',tags=['recherche'])

@router.get("/search-indicateur")
def search(query):
    
    #Authorize.jwt_required()
    #user_id = Authorize.get_jwt_subject()
    
    return message_service.recherche_consolider(query,query,['indicateur'])

@router.get("/search-rapport",response_model=RapportList)
def search(query):
    
    #Authorize.jwt_required()
    #user_id = Authorize.get_jwt_subject()
    
    return message_service.recherche_consolider(query,query,['rapport'])

app.include_router(router)
