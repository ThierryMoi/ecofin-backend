from pymongo import MongoClient
from bson import ObjectId
from model.user_model import UserInDB, UserUpdate, UserReadDB,UserReadSimple,OtpModel,StatusEnum
from typing import List
from configuration.properties import logger
from datetime import datetime
import re


class UserRepository:
    
    def __init__(self, collection,collection_otp):
        self.collection = collection
        self.logger = logger 
        self.collection_otp = collection_otp

    def add_user(self, user_data: UserInDB) -> str:
        try:
            user_dict = user_data.dict(exclude_unset=True)
            result = self.collection.insert_one(user_dict)
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f'Error while adding user: {str(e)}')
            raise

    def find_user_by_username(self, username):
        return self.collection.find_one({"username": username})
    
    def get_user_by_email(self, email: str) -> UserReadDB:
        try:
            user = self.collection.find_one({"email": email, "supprime": False})
            if user!=None:
                user["id_user"] = str(user.get("_id"))
            return UserReadSimple(**user) if user else None
        except Exception as e:
            self.logger.error(f'Error while getting user by email: {str(e)}')
            raise

    def get_user_password(self, user_id: str) -> UserReadDB:
        try:
            user = self.collection.find_one({"_id": ObjectId(user_id), "supprime": False})
            if user!=None:
                user["id_user"] = str(user.get("_id"))
            return UserReadSimple(**user) if user else None
        except Exception as e:
            self.logger.error(f'Error while getting user by email: {str(e)}')
            raise

    def get_user(self, user_id: str) -> UserReadDB:
        try:
            # verify user
            user = self.collection.find_one({"_id": ObjectId(user_id), "supprime": False})
            print(user)
            if user!=None:
                user["id_user"] = str(user.get("_id"))
            return UserReadDB(**user) if user else None
        except Exception as e:
            self.logger.error(f'Error while getting user by ID: {str(e)}')
            raise

    def update_user(self, user_id: str, user_data: dict) -> UserReadDB:
        try:
            user_updated = self.collection.update_one({"_id": ObjectId(user_id),"supprime": False}, {"$set": user_data})
            return user_updated.modified_count > 0
        except Exception as e:
            self.logger.error(f'Error while updating user: {str(e)}')
            raise

    def delete_user(self, user_id: str) -> bool:
        try:
            result = self.collection.update_one({"_id": ObjectId(user_id),"supprime": False}, {"$set": {"supprime": True,"deleted_at": datetime.datetime.now()}})
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f'Error while deleting user: {str(e)}')
            raise

    def find_users(self, query: dict) -> List[UserReadDB]:
        try:
            query["supprime"] = False
            users = self.collection.find(query)
            return [UserReadDB(**user) for user in users]
        except Exception as e:
            self.logger.error(f'Error while finding users: {str(e)}')
            raise
        
    def find_one_user(self, query: dict) -> UserReadDB:
        try:
            query["supprime"] = False
            query["status"] = StatusEnum.active.value
            user = self.collection.find_one(query)
            if user!=None:
                user["id_user"] = str(user.get("_id"))
            return UserReadDB(**user) if user else None
        except Exception as e:
            self.logger.error(f'Error while finding users: {str(e)}')
            raise

    def add_otp(self, otp: OtpModel) -> str:
        try:
            otp_dct = otp.dict(exclude_unset=True)
            result = self.collection_otp.insert_one(otp_dct)
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f'Error while adding user: {str(e)}')
            raise
        
    def get_otp_user(self, query: dict) -> OtpModel:
        try:
            otp_object = self.collection_otp.find_one(query)
            return OtpModel(**otp_object) if otp_object else None
        except Exception as e:
            self.logger.error(f'Error while getting user by ID: {str(e)}')
            raise
    
    def delete_opt(self, query) -> bool:
        try:
            result = self.collection_otp.delete_one(query)
            return True
        except Exception as e:
            self.logger.error(f'Error while deleting user: {str(e)}')

    def search_users(self, query: str) -> List[UserInDB]:

        regex_pattersearn = re.compile(query, re.IGNORECASE)
        users = list(self.collection.find({"$or": [{"nom": {"$regex": regex_pattersearn}}, {"prenom": {"$regex": regex_pattersearn}}]}))
        lst = []
        if len(users)>0:
            for usr in users:
                usr["id_user"] = str(usr.get("_id"))
                lst.append(UserReadDB(**usr))
        return lst       
        
