from fastapi import APIRouter, Depends, HTTPException
from typing import List
from model.message_model import Message,MessageResponse
from configuration.properties import app

from configuration.posgres import CONNECTION_STRING



from service.message_service import MessageService
from repository.message_repository import MessageRepository


message_repository = MessageRepository(CONNECTION_STRING)
message_service = MessageService(message_repository)

router = APIRouter()


@router.post("/messages/", response_model=MessageResponse)
def create_user(message: MessageResponse):
    created_message = message_repository.create_message(message.dict())
    return created_message

@router.get("/messages/{message_id}", response_model=MessageResponse)
def get_message_by_id(message_id: str):
    message = message_service.get_message_by_id(message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message non trouvé")
    return message

@router.get("/messages/", response_model=List[MessageResponse])
def get_all_messages():
    return message_service.get_all_messages()

@router.put("/messages/{message_id}", response_model=MessageResponse)
def update_message( message_id: str, message: MessageResponse):
    updated_message = message_service.update_message(message_id, message)
    if updated_message is None:
        raise HTTPException(status_code=404, detail="Message non trouvé")
    return updated_message

@router.delete("/messages/{message_id}")
def delete_message(message_id: str):
    deleted_message = message_service.delete_message(message_id)
    if deleted_message is None:
        raise HTTPException(status_code=404, detail="Message non trouvé")
    return {"message": "Message supprimé avec succès"}

app.include_router(router)
