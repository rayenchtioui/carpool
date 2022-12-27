import uuid
from operator import and_, or_
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..routers.emailUtil import send_email
from datetime import timedelta, datetime
from sqlalchemy.exc import SQLAlchemyError
from ..config import settings
from app import schemas, models, utils, enums, oauth2
from .error import add_error

router = APIRouter(
    prefix="/pooling",
    tags=['Pooling']
)


@router.post('/', response_model=schemas.PoolOut, status_code=status.HTTP_201_CREATED)
def create_pooling(pooling: schemas.Pool, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    # verify that the car id given in the request exists and belongs to the current user logged in
    db_car = db.query(models.Car).filter(
        and_(models.Car.id == pooling.car_id, models.Car.owner_id == current_user.id)).first()

    if not db_car:
        return schemas.PoolOut(
            status=status.HTTP_404_NOT_FOUND,
            message="You have to choose an available car to create a pooling post"
        )
    try:
        db_pooling = models.Pooling(
            driver_id=current_user.id, **pooling.dict())
        db.add(db_pooling)
        db.commit()
        db.refresh(db_pooling)
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.PoolOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="There is a problem try again"
        )
    return schemas.PoolOut(
        **db_pooling.__dict__,
        status=status.HTTP_201_CREATED,
        message="Pooling created successfully"
    )
