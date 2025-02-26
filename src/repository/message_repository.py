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

    def find_all_by_user_discussion(self, user_id, discussion_id, page, page_size):
        # Gestion des pages
        if page < 1:
            page = 1  # On évite les pages négatives ou 0
        skip = (page - 1) * page_size

        # Requête MongoDB pour récupérer les messages filtrés
        query_filter = {
            "deleted_at": {"$exists": False},
            "user_id": user_id,
            "discussion_id": discussion_id
        }
        msgs = list(self.collection.find(query_filter)
                    .sort("created_at", -1)
                    .skip(skip)
                    .limit(page_size))

        # Transformation des messages (conversion de _id en message_id)
        lst = []
        for msg in msgs:
            msg["message_id"] = str(msg.get("_id"))
            lst.append(msg)

        # Calcul du nombre total de documents avec les mêmes critères de filtre
        nombre_total = self.collection.count_documents(query_filter)

        # Calcul du nombre de pages total
        nombre_de_pages = (nombre_total + page_size - 1) // page_size

        return lst, nombre_de_pages


    def nb_message_by_user_by_discussion(self, user_id, discussion_id):
        # Filtre de la requête
        query_filter = {
            "deleted_at": {"$exists": False},
            "user_id": user_id,
            "discussion_id": discussion_id
        }

        # Compte le nombre total de messages
        total_messages = self.collection.count_documents(query_filter)

        # Si le nombre est un multiple de 5, récupérer les 5 derniers messages
        if total_messages < 10 or total_messages % 5 == 0:
            # Récupérer les 5 derniers messages
            last_five_messages = list(self.collection.find(query_filter)
                                    .sort("created_at", -1)
                                    .limit(10))
            
            # Transformer les messages pour inclure message_id
            for msg in last_five_messages:
                msg["message_id"] = str(msg.get("_id"))
            
            return last_five_messages
        
        # Sinon, on retourne simplement le nombre de messages
        return None




    def find_by_id(self, message_id: str) -> MessageRead:
        message_data = self.collection.find_one({"_id": ObjectId(message_id)})
        return MessageRead(**message_data) if message_data else None

    def update_response(self, message_id: str, response: str) -> bool:
        result = self.collection.update_one({"_id": ObjectId(message_id)}, {"$set": {"response": response, "updated_at": datetime.utcnow()}})
        return result.modified_count > 0
