from fastapi import Depends, HTTPException, APIRouter, status
from pydantic import BaseModel
from typing import List,Optional
from bson import ObjectId
from service.user_service import UserService
from service.password_service import PasswordResetService
from model.user_model import  UserCreate,ConnectionType, UserReadDB, OtpModel, UserUpdate, StatusEnum, UserMdp, PasswordResetRequest, PasswordResetToken


from configuration.properties import app,logger
from configuration.mongo import USER_COLLECTION, OTP_COLLECTION, PASSWORD_RESET_COLLECTION
from repository.user_repository import UserRepository
import pyotp
from service.auth_service import AuthJWT
from configuration.security import PWD_CONTEXT
from service.validation import EmailService, CodeController


from model.auth_model import UserAuth
from configuration.security import ACCESS_TOKEN_EXPIRES_IN, REFRESH_TOKEN_EXPIRES_IN
from datetime import datetime, timedelta




user_repository = UserRepository(USER_COLLECTION, OTP_COLLECTION)

email_service = EmailService()

user_service = UserService(user_repository)
service = PasswordResetService(USER_COLLECTION, PASSWORD_RESET_COLLECTION)


# Initialisation de l'APIRouter
router = APIRouter(prefix="/user", tags=["users"])

@router.post("/add")
def create_user(user: UserCreate, Authorize: AuthJWT = Depends()):
    """
    Point de terminaison pour créer un nouvel utilisateur.

    :param user: Objet modèle UserCreate contenant les détails de l'utilisateur.
    :param Authorize: Instance de AuthJWT pour l'autorisation JWT.

    Returns:
    - dict: Réponse indiquant le statut de création de l'utilisateur.
    """
    response = dict()
    if len(user_repository.find_users({'email': user.email})) != 0:
        logger.error("La création de l'utilisateur a échoué : L'utilisateur existe déjà")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="L'utilisateur existe déjà")


    if user.password != user.confirm_password:
            logger.error("La création de l'utilisateur a échoué : Échec de validation du mot de passe")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Échec de validation du mot de passe")


    id_user = user_service.create_user(user)        

    db_user = user_repository.get_user_by_email(user.email)
    logger.info("Utilisateur créé avec succès")
    return {"id_user": db_user.id_user, "email_user": user.email}
    


@router.get("/get-one", response_model=UserReadDB)
def get_user(user_id: str, Authorize: AuthJWT = Depends()):
    """
    Point de terminaison pour obtenir les détails d'un utilisateur spécifique.

    :param user_id: ID de l'utilisateur à récupérer.
    :param Authorize: Instance de AuthJWT pour l'autorisation JWT.

    Returns:
    - UserReadDB: Détails de l'utilisateur.
    """
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()

    if len(user_repository.find_users({'_id': ObjectId(user_id)})) == 0:
        logger.error("L'utilisateur n'existe pas")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="L'utilisateur n'existe pas")
    else:
        user_model = get_user(current_user_id, user_id)
        if user_model.status == StatusEnum.active:
            return user_model
        elif user_model.status == StatusEnum.inactive:
            logger.error("Compte utilisateur non activé")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Compte utilisateur non activé")
        else:
            logger.error("Utilisateur banni")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Utilisateur banni")

@router.patch("/update", response_model=dict)
def update_user(user: UserUpdate,Authorize: AuthJWT = Depends()):
    """
    Point de terminaison pour mettre à jour les détails de l'utilisateur.

    :param user: Dictionnaire contenant les détails de l'utilisateur mis à jour.
    :param Authorize: Instance de AuthJWT pour l'autorisation JWT.

    Returns:
    - dict: Réponse indiquant le statut de la mise à jour.
    """
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    response = dict()

    if len(user_repository.find_users({'_id': ObjectId(current_user_id)})) == 0:
        logger.error("L'utilisateur n'existe pas")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="L'utilisateur n'existe pas")
    else:
        updated_user = user_service.update_user(current_user_id, user,background_tasks)
        response["code"] = status.HTTP_200_OK
        if updated_user=="stop":
            raise HTTPException(status_code=403, detail="Les informations de residence ne peuvent etre modifier")

        if updated_user:    
            response["message"] = "Utilisateur mis à jour avec succès"
            return response
        else:
            response["message"] = "Modification déjà effectuée"
            return response

@router.delete("/delete")
def delete_user(Authorize: AuthJWT = Depends()):
    """
    Point de terminaison pour supprimer un utilisateur.

    :param Authorize: Instance de AuthJWT pour l'autorisation JWT.

    Returns:
    - dict: Réponse indiquant le statut de la suppression.
    """
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    response = dict()
    if len(user_repository.find_users({'_id': ObjectId(current_user_id)})) == 0:
        logger.error("L'utilisateur n'existe pas")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="L'utilisateur n'existe pas")
    else:
        user_delete = user_service.delete_user(current_user_id)
        response["message"] = "Utilisateur supprimé avec succès"
        return response




@router.put("/update-mdp", response_model=dict)
def update_mdp_user(mdp_update: UserMdp, Authorize: AuthJWT = Depends()):
    """
    Point de terminaison pour mettre à jour le mot de passe utilisateur.

    :param mdp_update: Objet modèle UserMdp contenant les détails des anciens et nouveaux mots de passe.
    :param Authorize: Instance de AuthJWT pour l'autorisation JWT.

    Returns:
    - dict: Réponse indiquant le statut de mise à jour du mot de passe.
    """
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    response = dict()
    db_user = user_repository.get_user_password(current_user_id)
    if not PWD_CONTEXT.verify(mdp_update.old_password, db_user.hashed_password):
        logger.error("Ancien mot de passe incorrect")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ancien mot de passe incorrect")
    elif mdp_update.new_password != mdp_update.confirm_password:
        logger.error("Échec de validation du nouveau mot de passe")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Échec de validation du nouveau mot de passe")
    else:
        user_service.update_user(current_user_id, {'hashed_password': PWD_CONTEXT.hash(mdp_update.new_password)})
    response["code"] = status.HTTP_200_OK
    response["message"] = "Mot de passe mis à jour avec succès"
    return response

@router.post("/request-password-reset/")
def request_password_reset(request: PasswordResetRequest):
    """
    Point de terminaison pour demander une réinitialisation de mot de passe.

    :param request: Objet modèle PasswordResetRequest contenant l'e-mail pour la réinitialisation de mot de passe.

    Returns:
    - dict: Réponse indiquant le statut de la demande de réinitialisation de mot de passe.
    """
    result = service.request_password_reset(request.email)
    message = result["token"]
    email_service.send_email(request.email, "Réinitialiser le mot de passe", message)
    return {"message": result["message"]}

@router.post("/password-reset/")
def reset_password(token_data: PasswordResetToken, new_password: str):
    """
    Point de terminaison pour réinitialiser le mot de passe de l'utilisateur.

    :param token_data: Objet modèle PasswordResetToken contenant les données du jeton pour la réinitialisation de mot de passe.
    :param new_password: Nouveau mot de passe à définir.

    Returns:
    - dict: Réponse indiquant le statut de réinitialisation de mot de passe.
    """
    result = service.reset_password(token_data.token, new_password)
    return {"message": result["message"]}



@router.get("/search", response_model=List[UserReadDB])
def search(query:str, Authorize: AuthJWT = Depends()):
    """
    Récupère toutes les publications.

    Returns:
 List[PublicationReadBd]: Liste de toutes les instances de la classe PublicationReadBd.
    """
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()    
    users = user_service.get_user_search(query,current_user_id)
    return users


app.include_router(router)
