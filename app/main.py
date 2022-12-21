from fastapi import FastAPI
from .routers import auth
from fastapi.middleware.cors import CORSMiddleware
from app.database import SessionLocal, engine
from app.models import Base

Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}
