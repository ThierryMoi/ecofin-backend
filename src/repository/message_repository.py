from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from  model.message_model import MessageBase, MessageRead, MessageResponse

class MessageRepository:
    def __init__(self,  collection):
        self.collection = collection

    def create(self, message: MessageBase) -> str:
        message_data = message.dict()
        message_data['created_at'] = datetime.utcnow()
        result = self.collection.insert_one(message_data)
        return str(result.inserted_id)

    def find_by_id(self, message_id: str) -> MessageRead:
        message_data = self.collection.find_one({"_id": ObjectId(message_id)})
        return MessageRead(**message_data) if message_data else None

    def update_response(self, message_id: str, response: str) -> bool:
        result = self.collection.update_one({"_id": ObjectId(message_id)}, {"$set": {"response": response, "updated_at": datetime.utcnow()}})
        return result.modified_count > 0
