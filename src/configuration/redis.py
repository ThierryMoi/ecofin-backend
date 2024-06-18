
import os
from redis import Redis
from dotenv import load_dotenv

# Chargez les variables d'environnement depuis le fichier .env
load_dotenv()


redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
redis_bd = os.environ.get("REDIS_BD", 0)

REDIS_CONN = Redis(host=redis_host, port=redis_port, db=redis_bd, decode_responses=True)
# Utilisez une structure de données pour stocker les utilisateurs connectés
connected_users = {}
