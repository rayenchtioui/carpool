from operator import and_, or_
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, aliased
from ..database import get_db
from datetime import timedelta, datetime
from sqlalchemy.exc import SQLAlchemyError
from ..config import settings
from app import schemas, models, utils, enums, oauth2
from .error import add_error

router = APIRouter(
    prefix="/pooluser",
    tags=['PoolUsers']
)


@router.post('/apply-for-pool', response_model=schemas.PoolUserOut, status_code=status.HTTP_200_OK)
def apply_for_pool(pooling_id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    db_pool = db.query(models.Pooling).filter(
        models.Pooling.availability == True,
        models.Pooling.available_seats > 0).filter(
        models.Pooling.id == pooling_id).first()
    if not db_pool:
        return schemas.PoolUserOut(
            pooling_id=pooling_id,
            user_id=current_user.id,
            status=status.HTTP_404_NOT_FOUND,
            message="Pool unavailable"
        )
    try:
        db_pool.available_seats -= 1
        db_pool_user = models.PoolingUsers(
            pooling_id=pooling_id, user_id=current_user.id)
        db.add(db_pool_user)
        db.commit()
        db.refresh(db_pool_user)
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.PoolUserOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="There is a problem try again"
        )
    return schemas.PoolUserOut(
        **db_pool_user.__dict__,
        status=status.HTTP_201_CREATED,
        message="you applied for the pool successfully and you seat is reserved"
    )


@router.get('pools-applied-for/', response_model=schemas.PoolsUserOut, status_code=status.HTTP_200_OK)
def get_user_applied_pools(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    db_pool = db.query(models.PoolingUsers).filter(
        models.PoolingUsers.user_id == current_user.id)
    if not db_pool:
        return schemas.PoolsUserOut(
            status=status.HTTP_404_NOT_FOUND,
            message="No pools available"
        )
    results = (
        db.query(models.PoolingUsers, models.User, models.Pooling, models.Car)
        .join(models.User, models.User.id == models.PoolingUsers.user_id)
        .join(models.Pooling, models.Pooling.id == models.PoolingUsers.pooling_id)
    ).all()
    pooling_user_list = []

    for result in results:
        pooling_user = schemas.PoolingUserOut(
            pooling_id=result[0].pooling_id,
            user_id=result[0].user_id,
            driver_name=result[1].first_name,
            driver_last_name=result[1].last_name,
            driver_phone=result[1].phone,
            car_name=result[3].car_name,
            price=result[2].price
        )
        pooling_user_list.append(pooling_user)
    return schemas.PoolsUserOut(pooling_list=pooling_user_list, message="success", status=200)


@router.delete('cancel-pool/', response_model=schemas.PoolUserOut, status_code=status.HTTP_200_OK)
def cancel_pool(pooling_id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    db_pool = db.query(models.PoolingUsers).filter(
        and_(models.PoolingUsers.pooling_id == pooling_id, models.PoolingUsers.user_id == current_user.id)).first()
    pool_to_delete = db_pool
    if not db_pool:
        return schemas.PoolUserOut(
            status=status.HTTP_404_NOT_FOUND,
            message="Pool not found!"
        )
    try:
        db_pool = db.query(models.Pooling).filter(
            models.Pooling.id == pooling_id).first()
        db_pool.available_seats += 1
        db.delete(db_pool)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e)
        return schemas.PoolUserOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Something went wrong"
        )
    return schemas.PoolUserOut(
        **pool_to_delete.__dict__,
        status=status.HTTP_202_ACCEPTED,
        message="Pool deleted successfully"
    )
