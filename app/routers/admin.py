from fastapi import APIRouter, Depends, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from datetime import timedelta, datetime
from sqlalchemy.exc import SQLAlchemyError
from .resetCode import add_reset_code, send_reset_code_email, get_reset_password_code, reset_password, disable_reset_code
from ..config import settings
from app import oauth2
from .error import add_error
from app import schemas, models, utils, enums

router = APIRouter(
    prefix="/admin",
    tags=['Admin']
)


@router.post('/login', response_model=schemas.Token)
def login_admin(admin_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(
        models.Admin.email == admin_credentials.username).first()
    if not admin:
        return schemas.Token(
            message="Invalid Credentials",
            status=status.HTTP_404_NOT_FOUND
        )
    if not utils.verify(admin_credentials.password, admin.password):
        return schemas.Token(
            message="Invalid Credentials",
            status=status.HTTP_403_FORBIDDEN
        )
    data = {
        "user": {
            "id": admin.id,
            "email": admin.email,
        }
    }
    access_token = oauth2.create_access_token(data=data)
    return schemas.Token(access_token=access_token,
                         token_type="bearer",
                         status=status.HTTP_200_OK
                         )


@router.get('/all-users', response_model=schemas.UsersOut, status_code=status.HTTP_200_OK)
def get_all_users(db: Session = Depends(get_db), current_admin=Depends(oauth2.get_current_admin)):
    db_users = db.query(models.User).all()
    if not db_users:
        return schemas.UsersOut(
            status=status.HTTP_404_NOT_FOUND,
            message="No users found!"
        )
    return schemas.UsersOut(
        users_list=[schemas.UserOut(**user.__dict__) for user in db_users],
        message="all users",
        status=status.HTTP_200_OK
    )


@router.get('/all-pools', status_code=status.HTTP_200_OK)
def get_all_pools(db: Session = Depends(get_db), current_admin=Depends(oauth2.get_current_admin)):
    db_pools = db.query(models.Pooling).all()
    if not db_pools:
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "message": "No pools found!"
        }
    return {
        "pool_list": [schemas.PoolOut(**pool.__dict__) for pool in db_pools],
        "message": "all users",
        "status": status.HTTP_200_OK
    }


@router.delete('/delete-user', status_code=status.HTTP_200_OK)
def delete_user(id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == id).first()
    user_to_delete = db_user
    if not db_user:
        return schemas.UserOut(
            status=status.HTTP_404_NOT_FOUND,
            message="user with id {0} is not found".format(id)
        )
    try:
        db.delete(db_user)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.UserOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="There is a problem try again"
        )
    return schemas.UserOut(
        **user_to_delete.__dict__,
        status=status.HTTP_202_ACCEPTED,
        message="account has been deleted successfully"
    )


@router.delete('/delete-pool/{id}', response_model=schemas.PoolOut, status_code=status.HTTP_200_OK)
def delete_pool(id: int, db: Session = Depends(get_db), current_admin=Depends(oauth2.get_current_admin)):
    db_pool = db.query(models.Pooling).filter(
        models.Pooling.id == id).first()
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


@router.delete('/delete-review/{id}', response_model=schemas.ReviewOut, status_code=status.HTTP_200_OK)
def delete_review(id: int, db: Session = Depends(get_db), current_admin=Depends(oauth2.get_current_admin)):
    db_review = db.query(models.Review).filter(
        models.Review.id == id).first()
    review_to_delete = db_review
    if not db_review:
        return schemas.ReviewOut(
            status=status.HTTP_404_NOT_FOUND,
            message="Review not found!"
        )
    try:
        db.delete(db_review)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e)
        return schemas.ReviewOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Something went wrong"
        )
    return schemas.ReviewOut(
        **review_to_delete.__dict__,
        status=status.HTTP_202_ACCEPTED,
        message="Review deleted successfully"
    )
