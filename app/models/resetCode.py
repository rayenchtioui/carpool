import datetime
from sqlalchemy import Integer, String, Column, DateTime, Enum
from ..enums import CodeStatus
from ..database import Base


class ResetCode(Base):
    __tablename__ = "reset_codes"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False)
    reset_code = Column(String, nullable=False)
    status = Column(Enum(CodeStatus), nullable=False)
    created_on = Column(DateTime, default=datetime.datetime.utcnow())
