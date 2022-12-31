from sqlalchemy import Date, Boolean, Column, ForeignKey, Integer, String, DateTime, Enum, Float
from sqlalchemy.orm import relationship

from app.database import Base
from app.enums import *


class PoolingUsers(Base):
    __tablename__ = 'pooling_users'
    pooling_id = Column(Integer, ForeignKey('pooling.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
