from fastapi import Depends, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, models, enums
import uuid
from ..routers.emailUtil import send_email


async def send_reset_code_email(email: str, reset_code: str):
    subject = "Reset Password"
    recipients = [email]
    await send_email(subject, recipients, enums.EmailTemplate.ResetPassword, email, reset_code)


def add_reset_code(email: str, db: Session = Depends(get_db)):
    reset_code = models.ResetCode(
        email=email,
        reset_code=str(uuid.uuid1()),
        status=enums.CodeStatus.pending
    )
    db.add(reset_code)
    db.flush()
    return reset_code


def get_reset_password_code(reset_code: str, db: Session = Depends(get_db)):
    return db.query(models.ResetCode).filter(models.ResetCode.reset_code == reset_code).first()


def reset_password(email: str, new_hashed_password: str, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.email == email)
    user = user_query.first()
    if not user:
        return schemas.ResetPasswordOut(
            message="No user with this email",
            status=status.HTTP_404_NOT_FOUND
        )
    fields_to_update = schemas.UserResetPassword(
        email=user.email,
        password=new_hashed_password
    )
    user_query.update(fields_to_update.dict(), synchronize_session=False)


def disable_reset_code(reset_code: str, db: Session = Depends(get_db)):
    reset_code_query = db.query(models.ResetCode).filter(
        models.ResetCode.reset_code == reset_code)
    fields_to_update = schemas.ResetCodeDeactivate(
        status=enums.CodeStatus.used)
    reset_code_query.update(fields_to_update.dict(), synchronize_session=False)
