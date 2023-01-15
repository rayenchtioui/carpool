from sqlalchemy import Column, Integer, String, DateTime
from ..database import Base

class JWTblacklist(Base):
    __tablename__ = "JWT_blacklist"
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True)
    expired_on = Column(DateTime)
