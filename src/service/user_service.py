from repository.user_repository import UserRepository
from model.user_model import UserCreate, UserReadDB,ConnectionType, UserUpdate, UserInDB, StatusEnum, OtpModel,UserUpdateInBD
from fastapi import HTTPException,BackgroundTasks
from datetime import datetime
from configuration.security import PWD_CONTEXT
from service.validation import EmailService, CodeController 
import base64
import io
import re
import pyotp
from configuration.properties import logger
from bson import ObjectId
from template.add_user_email import generate_html_success
from template.user_communaute import generate_html_new_member


# Initialiser le service de gestion des fichiers Minio
email_service = EmailService()
code_controller = CodeController(email_service)


class UserService:
    
    def __init__(self, user_repository,):
        self.user_repository = user_repository

                
    def generate_unique_username(self, nom, prenom):
        base_username = self._generate_base_username(nom, prenom)
        username = base_username
        suffix = 1

        while self.user_repository.find_user_by_username(username):
            username = f"{base_username}{suffix}"
            suffix += 1

        return username

    def _generate_base_username(self, nom, prenom):
        nom_parts = re.findall(r'\w+', nom.lower())
        prenom_parts = re.findall(r'\w+', prenom.lower())

        # Construction du nom d'utilisateur en utilisant les parties du nom et du prénom
        base_username = "".join([part for part in nom_parts])
        if len(prenom_parts) > 0:
            base_username += prenom_parts[0]

        return base_username

    def create_user(self, user_data: UserCreate):
        """
        Crée un nouvel utilisateur.

        :param user_data: Données de l'utilisateur à créer.
        """
        user_with_hash = UserInDB(**user_data.dict(), hashed_password=PWD_CONTEXT.hash(user_data.password))
        user_with_hash.supprime = False
        user_with_hash.status = StatusEnum.active
        user_with_hash.created_at = datetime.now()
        user_with_hash.username =self.generate_unique_username(user_with_hash.nom,user_with_hash.prenom)
        user_id = str(self.user_repository.add_user(user_with_hash))
        
        logger.info("Nouvel utilisateur créé avec succès")
        return "success"



    def get_user(self, user_id:str):
        return  self.user_repository.get_user(user_id)



    def update_user(self, user_id, user_data_controller,background_tasks):

        if type(user_data_controller) != dict:
            user_data = UserUpdateInBD(**user_data_controller.dict()) 
                   
            user_data.updated_at = datetime.now()
      
        elif type(user_data_controller) == dict:  # Remplacez MyClass par le nom de votre classe
            user_data = UserUpdateInBD(**user_data_controller) 

        result = self.user_repository.update_user(user_id, user_data.dict())
        # Gérer les fichiers
        logger.info("Détails de l'utilisateur mis à jour avec succès")
        return result

    def delete_user(self, user_id):
        """
        Supprime un utilisateur.

        :param user_id: ID de l'utilisateur à supprimer.
        """
        return self.user_repository.delete_user(user_id)

    def search_users(self, query):
        """
        Recherche des utilisateurs en fonction d'une requête donnée.

        :param query: Requête de recherche.

        Returns:
        - List[UserReadDB]: Liste des utilisateurs correspondant à la requête.
        """
        # Logique de filtrage ou de recherche supplémentaire
        return self.user_repository.find_users(query)



    def get_user_search(self,query:str,current_user_id):
        try:
            alluser=[]
            for usr in self.user_repository.search_users(query):
                alluser.append(self.get_user(current_user_id, usr.id_user))
            return alluser        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de toutes les publications: {e}")
            raise e
