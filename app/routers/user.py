from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database import get_db
from datetime import timedelta, datetime
from sqlalchemy.exc import SQLAlchemyError
from ..config import settings
from app import schemas


router = APIRouter(
    tags=['users'],
    Tags=['Users']
)


