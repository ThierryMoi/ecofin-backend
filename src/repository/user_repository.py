from pymongo import MongoClient
from bson import ObjectId
from typing import Optional, List
from datetime import datetime
from model.user_model import UserRead,UserBase,UserUpdate

class UserRepository:
    def __init__(self, collection):
        self.collection = collection

    def create(self, user_data: dict) -> str:
        if self.collection.find_one({"$or": [{"user_id": user_data["user_id"]}, {"deleted_at": {"$exists": True}}]}):
            raise ValueError("User with the same user_id or email already exists")
        user_data['created_at'] = datetime.utcnow()
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)

    def find_by_id(self, user_id: str) -> Optional[dict]:
        return self.collection.find_one({"user_id": user_id, "deleted_at": {"$exists": False}})

    def find_by_email(self, email: str) -> Optional[dict]:
        return self.collection.find_one({"email": email, "deleted_at": {"$exists": False}})

    def find_all(self) -> List[dict]:
        for e in self.collection.find({"deleted_at": {"$exists": False}}):
            print(UserRead(**e))
        return list(self.collection.find({"deleted_at": {"$exists": False}}))

    def update(self, user_id: str, update_data: dict) -> bool:
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one({"user_id": user_id, "deleted_at": {"$exists": False}}, {"$set": update_data})
        return result.modified_count > 0

    def delete(self, user_id: str) -> bool:
        result = self.collection.update_one({"user_id": user_id, "deleted_at": {"$exists": False}}, {"$set": {"deleted_at": datetime.utcnow()}})
        return result.modified_count > 0
