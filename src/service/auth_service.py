import base64
from typing import List
from fastapi import Depends, HTTPException, status,Request
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from bson.objectid import ObjectId
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from model.user_model import UserReadDB
from configuration.mongo import USER_COLLECTION,OTP_COLLECTION
from configuration.redis import REDIS_CONN
from configuration.security import *
from configuration.properties import app,logger
from repository.user_repository import UserRepository
from model.user_model import StatusEnum

user_repository = UserRepository(USER_COLLECTION,OTP_COLLECTION)

class Settings(BaseModel):
    authjwt_algorithm: str = JWT_ALGORITHM
    authjwt_decode_algorithms: List[str] = [JWT_ALGORITHM]
   # authjwt_token_location: set = {'cookies', 'headers'}
   # authjwt_access_cookie_key: str = 'access_token'
   # authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False

    authjwt_public_key: str = base64.b64decode(JWT_PUBLIC_KEY).decode('utf-8')
    authjwt_private_key: str = base64.b64decode(JWT_PRIVATE_KEY).decode('utf-8')
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access","refresh"}

@AuthJWT.load_config
def get_config():
    return Settings()

class NotVerified(Exception):
    pass

class UserNotFound(Exception):
    pass

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    entry = REDIS_CONN.get(jti)
    return entry and entry == 'true'

def require_user(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
        user = user_repository.get_user(str(user_id))

        if not user:
            logger.error('User no longer exists')
            raise UserNotFound('User no longer exists')

        if user.status==StatusEnum.inactive:
            logger.error('User is not verified')
            raise NotVerified('You are not verified')
        elif user.status==StatusEnum.banned:
            logger.error('User is banned')
            raise NotVerified('You are ban')


    except Exception as e:
        error = e.__class__.__name__
        logger.error(f'Error: {error}')
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='You are not logged in')
        if error == 'UserNotFound':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='User no longer exists')
        if error == 'NotVerified':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Please verify your account')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is invalid or has expired')
    return user_id
