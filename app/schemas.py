from pydantic import BaseModel, EmailStr
from typing import Optional

class OurBaseModel(BaseModel):
    class Config:
        orm_mode=True

class UserCreate(OurBaseModel):
    email: EmailStr
    password: str