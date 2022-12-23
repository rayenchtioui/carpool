import datetime
from sqlalchemy import Column, Integer, DateTime, String
from ..database import Base


class Error(Base):
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True, nullable=False)
    orig = Column(String, nullable=False)
    params = Column(String, nullable=False)
    statement = Column(String, nullable=False)
    created_on = Column(DateTime, default=datetime.datetime.utcnow())
