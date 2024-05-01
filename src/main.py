from fastapi.middleware.cors import CORSMiddleware

from configuration.properties import app,PORT
# from controller.user_controller import *
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI






origins = ["*"]  

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

if __name__ == '__main__':
    uvicorn.run("__main__:app", host="0.0.0.0", port=8008, reload=True, workers=2)