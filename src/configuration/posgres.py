from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DBNAME = os.environ.get("DBNAME")

USERNAME = os.environ.get("USERNAME")

PASSWORD = os.environ.get("PASSWORD")

ENDPOINT = os.environ.get("ENDPOINT")

PORT = os.environ.get("PORT")

CONNECTION_STRING = "postgresql://"+USERNAME+":"+PASSWORD+"@"+ENDPOINT+":"+PORT+"/"+ DBNAME
engine = create_engine(CONNECTION_STRING)
connection = engine.connect()
#connection.execute("commit")
#connection.execute(f"CREATE DATABASE {DBNAME}")
connection.close()

