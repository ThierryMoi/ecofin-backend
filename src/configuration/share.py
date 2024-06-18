   
import os
from redis import Redis
from dotenv import load_dotenv

load_dotenv()


SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.ionos.fr")
SMTP_PORT = os.environ.get("SMTP_PORT", 465)
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")

