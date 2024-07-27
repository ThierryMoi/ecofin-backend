from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from  model.message_model import MessageBase, MessageRead, MessageResponse
from typing import Optional, List

class MessageRepository:
    def __init__(self,  collection):
        self.collection = collection

    def create(self, message: MessageBase) -> str:
        message_data = message.dict()
        message_data['created_at'] = datetime.utcnow()
        result = self.collection.insert_one(message_data)
        return str(result.inserted_id)

    def find_all_by_user_discussion(self,user_id ,discussion_id, page, page_size):
        if page==0:
            skip=0
        else:
            skip = (page - 1) * page_size
        msgs= list(self.collection.find({"deleted_at": {"$exists": False},'user_id':user_id,'discussion_id':discussion_id}).sort("created_at", -1).skip(skip).limit(page_size))
        lst=[]
        for msg in msgs:
            msg["message_id"] = str(msg.get("_id"))
            lst.append(msg)
        nombre_total_communautes = self.collection.count_documents({})
        nombre_de_pages = (nombre_total_communautes + page_size - 1) // page_size
        return lst,nombre_de_pages





    def find_by_id(self, message_id: str) -> MessageRead:
        message_data = self.collection.find_one({"_id": ObjectId(message_id)})
        return MessageRead(**message_data) if message_data else None

    def update_response(self, message_id: str, response: str) -> bool:
        result = self.collection.update_one({"_id": ObjectId(message_id)}, {"$set": {"response": response, "updated_at": datetime.utcnow()}})
        return result.modified_count > 0
