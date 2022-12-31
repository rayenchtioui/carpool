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
def get_all_users(db: Session = Depends(get_db)):
    db_users = db.query(models.User).all()
    if not db_users:
        return schemas.UsersOut(
            status=status.HTTP_404_NOT_FOUND,
            message="No pools found!"
        )
    return schemas.UsersOut(
        users_list=[schemas.UserOut(**user.__dict__) for user in db_users],
        message="all users",
        status=status.HTTP_200_OK
    )
