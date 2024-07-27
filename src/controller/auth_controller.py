from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from configuration.properties import app, logger
from configuration.mongo import USER_COLLECTION, OTP_COLLECTION
from configuration.security import PWD_CONTEXT, ACCESS_TOKEN_EXPIRES_IN, REFRESH_TOKEN_EXPIRES_IN
from configuration.redis import REDIS_CONN
from model.user_model import StatusEnum,ConnectionType
from model.auth_model import LoginUserSchema, UserAuth
from service.auth_service import AuthJWT, require_user
from repository.user_repository import UserRepository

from datetime import datetime

from service.user_service import UserService



# Initialize repositories and services
user_repository = UserRepository(USER_COLLECTION, OTP_COLLECTION)


user_service = UserService(user_repository)

router = APIRouter(prefix="/auth", tags=["authentication"])


INCORRECT_CREDENTIALS_ERROR = 'Incorrect Email or Password'
USER_NOT_VERIFIED_ERROR = 'User is not verified'
USER_BANNED_ERROR = 'User banned'
INVALID_TOKEN_ERROR = 'Token not valid'


@router.post('/login',response_model=UserAuth)
def login(payload: LoginUserSchema, Authorize: AuthJWT = Depends()):
    """
    Endpoint to authenticate a user and generate access and refresh tokens.

    :param payload: LoginUserSchema model object containing user credentials.
    :param Authorize: Instance of AuthJWT for JWT authorization.
    :param firebase_service: Instance of FirebaseService for Firebase related operations.

    Returns:
    - UserAuth: User authentication details including access and refresh tokens.
    """
    db_user = user_repository.get_user_by_email(payload.email)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INCORRECT_CREDENTIALS_ERROR)

    # Vérification du statut de l'utilisateur
    if db_user.status == StatusEnum.inactive:
        logger.error(USER_NOT_VERIFIED_ERROR)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=USER_NOT_VERIFIED_ERROR)
    elif db_user.status == StatusEnum.banned:
        logger.error(USER_BANNED_ERROR)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=USER_BANNED_ERROR)

        # Si la connexion est de type simple, vérifier les identifiants
    if not db_user or not PWD_CONTEXT.verify(payload.password, db_user.hashed_password):
            logger.error(INCORRECT_CREDENTIALS_ERROR)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INCORRECT_CREDENTIALS_ERROR)

    
    db_user= user_service.get_user(db_user.id_user)
    # Création des tokens
    access_token = Authorize.create_access_token(
        subject=str(db_user.id_user), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))
    refresh_token = Authorize.create_refresh_token(
        subject=str(db_user.id_user), expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN))


    return UserAuth(**db_user.dict(), access_token=access_token,time_access_token=ACCESS_TOKEN_EXPIRES_IN, refresh_token=refresh_token,time_refresh_token=REFRESH_TOKEN_EXPIRES_IN)

@router.get('/refresh',response_model=dict)
def refresh_token(Authorize: AuthJWT = Depends()):
    """
    Endpoint to refresh the access token using the refresh token.

    :param Authorize: Instance of AuthJWT for JWT authorization.

    Returns:
    - dict: New access token.
    """
    try:
        Authorize.jwt_refresh_token_required()

        user_id = Authorize.get_jwt_subject()
        if not user_id:
            logger.error('Could not refresh access token: No user ID found')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not refresh access token')
        db_user = user_repository.get_user(str(user_id))

        if not db_user:
            logger.error('The user belonging to this token no longer exists')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='The user belonging to this token no longer exists')
        access_token = Authorize.create_access_token(
            subject=str(db_user.id_user), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))
    # stock dans elastic
        ES_CLIENT.index(index=INDEX_AUTH, body={"information": "reconnection à l'application","user":user_id, "date": datetime.now()}, default=serial)

        return {'access_token': access_token}
    except HTTPException as http_exc:
        logger.error(f'HTTPException: {http_exc.detail}')
        raise http_exc
    except Exception as e:
        logger.error(f'An error occurred: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete('/access-revoke',response_model=dict)
def access_revoke(Authorize: AuthJWT = Depends()):
    """
    Endpoint to revoke access token.

    :param Authorize: Instance of AuthJWT for JWT authorization.

    Returns:
    - dict: Confirmation message.
    """
    Authorize.jwt_required()

    jti = Authorize.get_raw_jwt()['jti']
    user_id = Authorize.get_jwt_subject()

    REDIS_CONN.setex(jti, ACCESS_TOKEN_EXPIRES_IN, 'true')
    # stock dans elastic
    ES_CLIENT.index(index=INDEX_AUTH, body={"information": "deconnecxion à l'application","user":user_id, "date": datetime.now()}, default=serial)

    return {"detail": "Access token has been revoked"}

@router.delete('/refresh-revoke', response_model=dict)
def refresh_revoke(Authorize: AuthJWT = Depends()):
    """
    Endpoint to revoke refresh token.

    :param Authorize: Instance of AuthJWT for JWT authorization.

    Returns:
    - dict: Confirmation message.
    """
    Authorize.jwt_refresh_token_required()

    jti = Authorize.get_raw_jwt()['jti']
    user_id = Authorize.get_jwt_subject()

    REDIS_CONN.setex(jti, REFRESH_TOKEN_EXPIRES_IN, 'true')
    # stock dans elastic
    ES_CLIENT.index(index=INDEX_AUTH, body={"information": "deconnecxion à l'application","user":user_id, "date": datetime.now()}, default=serial)
    return {"detail": "Refresh token has been revoked"}


# Include the router in the main FastAPI app
app.include_router(router)

