from fastapi import FastAPI
from .routers import auth, user, car, pooling, review, poolUser, admin
from fastapi.middleware.cors import CORSMiddleware
from app.database import SessionLocal, engine
from app.models import Base

app = FastAPI()
app_admin = FastAPI()

app_admin.include_router(admin.router)
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(car.router)
app.include_router(pooling.router)
app.include_router(review.router)
app.include_router(poolUser.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
