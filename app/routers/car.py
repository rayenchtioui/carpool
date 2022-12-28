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


@router.delete("/delete", response_model=schemas.CarOut, status_code=status.HTTP_200_OK)
def delete_car(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    # query to verify that the Car id exists and belongs to current user logged
    db_car = db.query(models.Car).filter(
        and_(models.Car.id == id, models.Car.owner_id == current_user.id)).first()
    car_to_delete = db_car
    if not db_car:
        return schemas.CarOut(
            status=status.HTTP_404_NOT_FOUND,
            message="Car not found!"
        )
    try:
        db.delete(db_car)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.CarOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Something went wrong"
        )
    return schemas.CarOut(
        **car_to_delete.__dict__,
        status=status.HTTP_202_ACCEPTED,
        message="Car Deleted successfully "
    )


@router.get('/get_cars', response_model=schemas.CarsOut, status_code=status.HTTP_200_OK)
def get_cars(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    db_cars = db.query(models.Car).filter(
        models.Car.owner_id == current_user.id).all()
    if not db_cars:
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "message": "No cars were found yet!"
        }
    return schemas.CarsOut(
        car_list=[schemas.CarOut(**car.__dict__) for car in db_cars],
        message="all cars",
        status=status.HTTP_200_OK
    )


@router.patch('/{id}', response_model=schemas.CarOut, status_code=status.HTTP_200_OK)
def update_car(id: int, car: schemas.EditCar, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    car_to_update = db.query(models.Car).filter(models.Car.id == id)
    db_car = car_to_update.first()
    if not db_car:
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Car not found"
        }
    try:
        car_data = car.dict(exclude_unset=True)
        for key, value in car_data.items():
            setattr(db_car, key, value)
        db.add(db_car)
        db.commit()
        db.refresh(db_car)
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.CarOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Something went wrong"
        )
    return schemas.CarOut(
        **db_car.__dict__,
        status=status.HTTP_200_OK,
        message="User updated successfully"
    )
