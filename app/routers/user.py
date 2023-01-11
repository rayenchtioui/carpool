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
from .confirmationCode import add_confirmation_code


router = APIRouter(
    prefix="/users",
    tags=['Users']
)


async def sendConfirmationMail(email: str, db: any):
    confirmation_code_to_add = schemas.ConfirmationCode(
        email=email, confirmation_code=str(uuid.uuid1()), status=enums.CodeStatus.pending)
    add_confirmation_code(confirmation_code_to_add, db)
    subject = "Account Confirmation"
    recipients = [email]
    await send_email(subject, recipients, enums.EmailTemplate.ConfirmAccount, email, confirmation_code_to_add.confirmation_code)


@router.post('/', response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.User, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.email == user.email).first()
    if db_user:
        return schemas.UserOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Email already used"
        )
    if user.password != user.confirmed_password:
        return schemas.UserOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Passwords must match"
        )
    try:
        hashed_password = utils.hash_password(user.password)
        user.password = hashed_password
        new_user_dict = user.dict()
        new_user_dict.pop('confirmed_password')
        new_user = models.User(**new_user_dict)
        db.add(new_user)
        db.flush()
        await sendConfirmationMail(user.email, db)
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.UserOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="There is a problem try again"
        )
    return schemas.UserOut(
        **new_user.__dict__,
        status=status.HTTP_201_CREATED,
        message="User created successfully and a confirmation email sent."

    )


@router.get('/{id}', response_model=schemas.UserOut, status_code=status.HTTP_200_OK)
def get_user(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    db_user = db.query(models.User).filter(models.User.id == id).first()
    if not db_user:
        return schemas.UserOut(
            status=status.HTTP_404_NOT_FOUND,
            message=f"User with id: {id} does not exist."
        )
    return schemas.UserOut(
        **db_user.__dict__,
        message=f"User with id {id}",
        status=status.HTTP_200_OK
    )


@router.patch('/{id}', response_model=schemas.UserOut, status_code=status.HTTP_200_OK)
def update_user(id: int, user: schemas.EditUser, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    user_to_update = db.query(models.User).filter(
        and_(models.User.id == id, current_user.id == id))
    db_user = user_to_update.first()
    if not db_user:
        return schemas.UserOut(
            status=status.HTTP_404_NOT_FOUND,
            message="User does not exist"
        )

    used_email = db.query(models.User).filter(
        and_(models.User.email == user.email, models.User.id != id))
    if used_email.first():
        return schemas.UserOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Email already used"
        )

    try:
        user_data = user.dict(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_user, key, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.UserOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Something went wrong"
        )
    return schemas.UserOut(
        **db_user.__dict__,
        status=status.HTTP_200_OK,
        message="User updated successfully"
    )


@router.delete('/delete_account', response_model=schemas.UserOut, status_code=status.HTTP_202_ACCEPTED)
def delete_user_account(user: schemas.UserDelete, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    if user.password != user.confirmed_password:
        return {
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Passwords must match"
        }
    hashed_password = utils.hash_password(user.password)
    db_user = db.query(models.User).filter(
        models.User.password == hashed_password).first()
    if not db_user:
        return schemas.Token(
            message="Invalid Credentials",
            status=status.HTTP_404_NOT_FOUND
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
    return {
        "status": status.HTTP_202_ACCEPTED,
        "message": "Your account has been deleted successfully"
    }
