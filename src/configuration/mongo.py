import os
import pymongo
from dotenv import load_dotenv

# Chargez les variables d'environnement depuis le fichier .env
load_dotenv()


mongo_host = os.environ.get("MONGO_HOST", "localhost")
mongo_port = int(os.environ.get("MONGO_PORT", 27017))
mongo_username = os.environ.get("MONGO_USERNAME")
mongo_password = os.environ.get("MONGO_PASSWORD")
mongo_database = os.environ.get("MONGO_DATABASE")


mongo_client = pymongo.MongoClient(
            mongo_host,
            mongo_port,
            username=mongo_username,
            password=mongo_password
        )
DATABASE = mongo_client[str(mongo_database)]
USER_COLLECTION = DATABASE["users"]
MESSAGE_COLLECTION = DATABASE["messages"]
DISCUSSION_COLLECTION = DATABASE["discussions"]

