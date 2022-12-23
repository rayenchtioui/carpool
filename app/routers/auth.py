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
from .confirmationCode import get_confirmation_code, confirm_account, disable_confirmation_code

router = APIRouter(
    tags=['Authentication']
)


@router.post('/login', response_model=schemas.Token)
def login_user(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if not user:
        return schemas.Token(
            message="Invalid Credentials",
            status=status.HTTP_404_NOT_FOUND
        )

    if not user.confirmed:
        return schemas.Token(
            message="Email has not been verified yet",
            status=status.HTTP_403_FORBIDDEN
        )

    if not utils.verify(user_credentials.password, user.password):
        return schemas.Token(
            message="Invalid Credentials",
            status=status.HTTP_403_FORBIDDEN
        )

    data = {
        "user": {
            "id": user.id,
            "email": user.email,
        }
    }


@router.post('/forgotPassword', response_model=schemas.ForgotPasswordOut)
async def forgot_password(user: schemas.ForgotPassword, db: Session = Depends(get_db)):
    email = db.query(models.User).filter(
        models.User.email == user.email).first()
    if not email:
        return schemas.ForgotPasswordOut(
            message="No account with this email",
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        reset_code = add_reset_code(user.email, db)
        db.flush()
        await send_reset_code_email(user.email, reset_code.reset_code)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.ForgotPasswordOut(
            message="Something went wrong",
            status=status.HTTP_400_BAD_REQUEST
        )

    return schemas.ForgotPasswordOut(
        message="email sent!",
        status=status.HTTP_200_OK
    )

    access_token = oauth2.create_access_token(data=data)
    return schemas.Token(access_token=access_token,
                         token_type="bearer",
                         status=status.HTTP_200_OK
                         )


@router.patch('/resetPassword', response_model=schemas.ResetPasswordOut)
def resetPassword(request: schemas.ResetPassword, db: Session = Depends(get_db)):
    reset_code = get_reset_password_code(request.reset_password_token, db)
    if not reset_code:
        return schemas.ResetPasswordOut(
            message="Reset link does not exist",
            status=status.HTTP_400_BAD_REQUEST
        )

    if reset_code.status == enums.CodeStatus.used:
        return schemas.ResetPasswordOut(
            message="Code Already Used",
            status=status.HTTP_400_BAD_REQUEST
        )

    expected_created_on = datetime.utcnow() + timedelta(minutes=-
                                                        settings.access_token_expire_min)
    if reset_code.created_on < expected_created_on:
        return schemas.ResetPasswordOut(
            message="Code expired",
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.new_password != request.confirm_new_password:
        return schemas.ResetPasswordOut(
            message="Passwords do not match",
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        new_hashed_password = utils.hash_password(request.new_password)
        reset_password(reset_code.email, new_hashed_password, db)
        disable_reset_code(request.reset_password_token, db)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.ResetPasswordOut(
            message="Something went wrong!",
            status=status.HTTP_400_BAD_REQUEST
        )

    return schemas.ResetPasswordOut(
        message="Password reset successfully",
        status=status.HTTP_200_OK
    )


@router.patch('/confirmAccount', response_model=schemas.ConfirmAccountOut)
def confirmAccount(request: schemas.ConfirmAccount, db: Session = Depends(get_db)):
    confirmation_code = get_confirmation_code(request.confirmation_code, db)
    if not confirmation_code:
        return schemas.ConfirmAccountOut(
            message="Confirmation code does not exist",
            status=status.HTTP_400_BAD_REQUEST
        )

    if confirmation_code.status == enums.CodeStatus.used:
        return schemas.ConfirmAccountOut(
            message='Account Already Confirmed',
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        confirm_account(confirmation_code.email, db)
        disable_confirmation_code(request.confirmation_code, db)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.UserOut(
            message="There is a problem, try again",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return schemas.ConfirmAccountOut(
        message="Account Confirmed",
        status=status.HTTP_200_OK
    )
