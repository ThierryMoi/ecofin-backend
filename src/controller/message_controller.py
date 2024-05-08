from fastapi import APIRouter, HTTPException
from model.message_model import MessageBase, MessageRead, MessageResponse

from configuration.properties import app

from configuration.openai import CLIENT_OPENAI

from configuration.mongo import MESSAGE_COLLECTION,USER_COLLECTION,DISCUSSION_COLLECTION
from service.message_service import MessageService

from repository.message_repository import MessageRepository
from utils.prompts import template_system,human_prompt

from fastapi import WebSocket, WebSocketDisconnect

from service.user_service import UserService

from repository.user_repository import UserRepository


user_repository = UserRepository(USER_COLLECTION)
user_service = UserService(user_repository)
from service.discussion_service import DiscussionService
from repository.discussion_repository import DiscussionRepository

discussion_repository = DiscussionRepository(DISCUSSION_COLLECTION)
discussion_service = DiscussionService(discussion_repository)


message_repository = MessageRepository(MESSAGE_COLLECTION)
message_service = MessageService(message_repository)
router = APIRouter(prefix='/messages')


@router.get("/get-one", response_model=MessageRead)
def read_message(message_id: str):
    message = message_service.get_message_by_id(message_id)
    if message:
        return message
    raise HTTPException(status_code=404, detail="Message not found")

@router.get("all-message-by-discusion-user")
def get_message_user_discussion(user_id: str, discussion_id: str,page :int , page_size:int ):
    if message_service.get_message_by_id(message_id):
        if message_service.respond_to_message(message_id, response.response):
            return True
        else:
            raise HTTPException(status_code=500, detail="Failed to respond to message")
    raise HTTPException(status_code=404, detail="Message not found")


@router.websocket("/chat")
async def chat_controller(ws: WebSocket):
    await ws.accept()
    while True:
        query = await ws.receive_json()
        #########################
        # si user existe ou pas
        # recuper la derniere historique du user
        
        articles_str, rapport_str =   message_service.consolidation_context(query.get("question"))

        usr= user_service.get_user_by_id(query.get("user_id"))
        if usr is None:
            usr = user_service.create_user({"user_id":query.get("user_id")})
        # recuperer l'historique
        disc= discussion_service.get_discussion_by_id(query.get("discussion_id"))
        if disc is None:
            print("Discussion")
            raise HTTPException(status_code=404, detail="Discussion not found")

        completion = CLIENT_OPENAI.chat.completions.create(
            model="gpt-3.5-turbo",
            stream=True,
            messages=[
                {"role": "system", "content": template_system},
                {"role": "user", "content": human_prompt(query.get("question"), articles_str, rapport_str)}
            ]
        )
        a=""
        for chunk in completion:
            response = chunk.choices[0].delta.content               
            if response:
                a = a+response
                print(a)
                await ws.send_text(str(response))
                
        message_service.create_message(MessageBase(discussion_id = query.get("discussion_id"),user_id=query.get("user_id"),response=a,question=query.get("question")))


app.include_router(router)
