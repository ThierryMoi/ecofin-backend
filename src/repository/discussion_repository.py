from pymongo import MongoClient
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

class DiscussionRepository:
    def __init__(self, collection):
        self.collection = collection

    def create(self, discussion_data: dict) -> str:     
        discussion_data['created_at'] = datetime.utcnow()
        result = self.collection.insert_one(discussion_data)
        return str(result.inserted_id)

    def find_by_id(self, discussion_id: str) -> Optional[dict]:
        disc= self.collection.find_one({"_id": ObjectId(discussion_id), "deleted_at": {"$exists": False}})
        if disc!=None:
            disc["discussion_id"] = str(disc.get("_id"))
        return disc

    def find_by_user_id(self, user_id: str) -> List[dict]:
        return list(self.collection.find({"user_id": user_id, "deleted_at": {"$exists": False}}))

    def find_all_by_user(self,user_id , page, page_size) -> List[dict]:
        if page==0:
            skip=0
        else:
            skip = (page - 1) * page_size
        discs= list(self.collection.find({"deleted_at": {"$exists": False},'user_id':user_id}).sort("created_at", -1).skip(skip).limit(page_size))
        lst=[]
        for disc in discs:
            disc["discussion_id"] = str(disc.get("_id"))
            lst.append(disc)
        nombre_total_communautes = self.collection.count_documents({})
        nombre_de_pages = (nombre_total_communautes + page_size - 1) // page_size
        return lst,nombre_de_pages


    def find_all(self,page, page_size) -> List[dict]:
        if page==0:
            skip=0
        else:
            skip = (page - 1) * page_size
        discs= list(self.collection.find({"deleted_at": {"$exists": False}}).sort("created_at", -1).skip(skip).limit(page_size))
        lst=[]
        for disc in discs:
            disc["discussion_id"] = str(disc.get("_id"))
            lst.append(disc)
        nombre_total_communautes = self.collection.count_documents({"supprime": False})
        nombre_de_pages = (nombre_total_communautes + page_size - 1) // page_size
        return lst,nombre_de_pages

    def update(self, discussion_id: str, update_data: dict) -> bool:
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one({"_id": ObjectId(discussion_id), "deleted_at": {"$exists": False}}, {"$set": update_data})
        return result.modified_count > 0

    def delete(self, discussion_id: str) -> bool:
        result = self.collection.update_one({"_id": ObjectId(discussion_id), "deleted_at": {"$exists": False}}, {"$set": {"deleted_at": datetime.utcnow()}})
        return result.modified_count > 0
