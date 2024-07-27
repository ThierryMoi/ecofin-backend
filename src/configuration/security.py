from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta

import os
from redis import Redis
from dotenv import load_dotenv

# Chargez les variables d'environnement depuis le fichier .env
load_dotenv()

OAUTH2_SCHEME= OAuth2PasswordBearer(tokenUrl="token")
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_PUBLIC_KEY = os.environ.get("JWT_PUBLIC_KEY")
JWT_PRIVATE_KEY =  os.environ.get("JWT_PRIVATE_KEY")

REFRESH_TOKEN_EXPIRES_IN = int(os.environ.get("REFRESH_TOKEN_EXPIRES_IN"))
ACCESS_TOKEN_EXPIRES_IN = int(os.environ.get("ACCESS_TOKEN_EXPIRES_IN"))
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
CLIENT_ORIGIN= os.environ.get("CLIENT_ORIGIN")
