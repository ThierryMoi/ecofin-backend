
from fastapi import FastAPI,BackgroundTasks
import os
import logging  

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"), 
        logging.StreamHandler()  
    ]
)

logger = logging.getLogger(__name__)
PORT = os.environ.get("PORT", 8000)


app = FastAPI()

