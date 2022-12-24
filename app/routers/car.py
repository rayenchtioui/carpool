from fastapi import APIRouter, Depends, status
from app import schemas, models, utils, enums, oauth2
from .error import add_error
from sqlalchemy.orm import Session
from ..database import get_db
from sqlalchemy.exc import SQLAlchemyError
from ..config import settings

router = APIRouter(
    prefix="/cars",
    tags=['Car']
)


@router.post('/', response_model=schemas.CarOut, status_code=status.HTTP_201_CREATED)
def create_car(car: schemas.Car, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    try:
        db_car = models.Car(owner_id=current_user.id, **car.dict())
        db.add(db_car)
        db.commit()
        db.refresh(db_car)
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.CarOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="There is a problem try again"
        )
    return schemas.CarOut(
        **db_car.__dict__,
        status=status.HTTP_201_CREATED,
        message="Car  created successfully."

    )
