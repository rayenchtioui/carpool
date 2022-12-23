from fastapi import Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, models, enums


def get_confirmation_code(confirmation_code: str, db: Session = Depends(get_db)):
    return db.query(models.ConfirmationCode).filter(models.ConfirmationCode.confirmation_code == confirmation_code).first()


def confirm_account(email: str, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.email == email)
    user = user_query.first()
    if not user:
        return schemas.ConfirmAccountOut(
            message="User with this email does not exist",
            status=status.HTTP_404_NOT_FOUND
        )
    fields_to_update = schemas.UserConfirm(confirmed=True)
    user_query.update(fields_to_update.dict(), synchronize_session=False)


def disable_confirmation_code(confirmation_code: str, db: Session = Depends(get_db)):
    confirmation_code_query = db.query(models.ConfirmationCode).filter(
        models.ConfirmationCode.confirmation_code == confirmation_code)
    code = confirmation_code_query.first()
    if not code:
        return schemas.ConfirmAccountOut(
            message="Confirmation code does not exist",
            status=status.HTTP_404_NOT_FOUND
        )
    fields_to_update = schemas.ConfirmationCodeDeactivate(
        status=enums.CodeStatus.used)

    confirmation_code_query.update(
        fields_to_update.dict(), synchronize_session=False)


def add_confirmation_code(confirmation_code: schemas.ConfirmationCode, db: Session = Depends(get_db)):
    confirmation_code = models.ConfirmationCode(**confirmation_code.dict())
    db.add(confirmation_code)
    db.flush()
    return confirmation_code
