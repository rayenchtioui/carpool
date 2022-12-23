from fastapi import Depends, status
from .. import models, schemas
from ..database import get_db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def add_error(e: SQLAlchemyError, db: Session = Depends(get_db)):
    error = models.Error(
        orig=str(e.__dict__['orig']),
        params=str(e.__dict__['params']),
        statement=str(e.__dict__['statement'])
    )
    try:
        db.add(error)
        db.commit()
        db.refresh(error)
    except SQLAlchemyError as e:
        db.rollback()
        return schemas.ErrorOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="something went wrong"
        )
    return schemas.ErrorOut(**error.__dict__,
                            status=status.HTTP_201_CREATED,
                            message="error added successfully"
                            )
