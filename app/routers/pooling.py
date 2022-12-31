import uuid
from operator import and_, or_
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, aliased
from ..database import get_db
from ..routers.emailUtil import send_email
from datetime import timedelta, datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import insert, delete
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


@router.get('/pool', response_model=schemas.PoolsOut, status_code=status.HTTP_200_OK)
def get_users_pools(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    db_pools = db.query(models.Pooling).filter(
        models.Pooling.driver_id == current_user.id
    ).all()
    if not db_pools:
        return schemas.PoolsOut(
            status=status.HTTP_404_NOT_FOUND,
            message="No pools found!"
        )
    return schemas.PoolsOut(
        pool_list=[schemas.PoolOut(**pool.__dict__) for pool in db_pools],
        message="all pools",
        status=status.HTTP_200_OK
    )


@router.get('/pools', response_model=schemas.PoolingOut, status_code=status.HTTP_200_OK)
def get_available_pools(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    db_pooling = db.query(models.Pooling).filter(
        models.Pooling.availability == True).all()
    if not db_pooling:
        return schemas.PoolingOut(
            status=status.HTTP_404_NOT_FOUND,
            message="No available pools"
        )
    rows = db.query(models.Pooling).filter(
        models.Pooling.date_depart < datetime.now()).all()
    if rows:
        for row in rows:
            pooling_history = models.PoolingHisotry(
                description=row.description,
                date_depart=row.date_depart,
                available_seats=row.available_seats,
                availability=row.availability,
                beg_dest=row.beg_dest,
                end_dest=row.end_dest,
                price=row.price,
                driver_id=row.driver_id,
                car_id=row.car_id)
            db.add(pooling_history)
            db.commit()
    stmt = delete(models.Pooling).where(
        models.Pooling.date_depart < datetime.now())
    db.execute(stmt)

    pools = db.query(models.Pooling, models.User, models.Car).join(
        models.User, models.Pooling.driver_id == models.User.id, isouter=True).join(
        models.Car, models.Pooling.car_id == models.Car.id, isouter=True).with_entities(
        models.Pooling.description,
        models.Pooling.date_depart,
        models.Pooling.available_seats,
        models.Pooling.availability,
        models.Pooling.beg_dest,
        models.Pooling.end_dest,
        models.Pooling.price,
        models.User.first_name.label("driver_first_name"),
        models.User.last_name.label("driver_last_name"),
        models.Car.car_name.label("car_name")
    ).all()
    pooling_out = schemas.PoolingOut()
    pooling_list = []

    for result in pools:
        pooling = schemas.Pooling()
        pooling.description = result.description
        pooling.date_depart = result.date_depart
        pooling.available_seats = result.available_seats
        pooling.availability = result.availability
        pooling.beg_dest = result.beg_dest
        pooling.end_dest = result.end_dest
        pooling.price = result.price
        pooling.driver_first_name = result.driver_first_name
        pooling.driver_last_name = result.driver_last_name
        pooling.car_name = result.car_name
        pooling_list.append(pooling)

    return schemas.PoolingOut(
        pooling_list=pooling_list,
        message="all pools",
        status=status.HTTP_200_OK
    )


@ router.delete('/delete/{id}', response_model=schemas.PoolOut, status_code=status.HTTP_200_OK)
def delete_pool(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    # query to verify that the pool id exists and belongs to the current user logged in
    db_pool = db.query(models.Pooling).filter(
        and_(models.Pooling.id == id, models.Pooling.driver_id == current_user.id)).first()
    pool_to_delete = db_pool
    if not db_pool:
        return schemas.PoolOut(
            status=status.HTTP_404_NOT_FOUND,
            message="Pool not found!"
        )
    try:
        db.delete(db_pool)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e)
        return schemas.PoolingOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Something went wrong"
        )
    return schemas.PoolOut(
        **pool_to_delete.__dict__,
        status=status.HTTP_202_ACCEPTED,
        message="Pool deleted successfully"
    )


@ router.patch('/{id}', response_model=schemas.PoolOut, status_code=status.HTTP_200_OK)
def update_pool(id: int, pool: schemas.EditPool, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):

    pool_to_update = db.query(models.Pooling).filter(
        and_(models.Pooling.id == id, models.Pooling.driver_id == current_user.id))
    db_pool = pool_to_update.first()
    if not db_pool:
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Pool not found"
        }
    try:
        pool_data = pool.dict(exclude_unset=True)
        for key, value in pool_data.items():
            setattr(db_pool, key, value)
        db.add(db_pool)
        db.commit()
        db.refresh(db_pool)
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.PoolOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Something went wrong"
        )
    return schemas.PoolOut(
        **db_pool.__dict__,
        status=status.HTTP_200_OK,
        message="Pool updated successfully"
    )
