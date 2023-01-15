from sqlalchemy import Column, ForeignKey, Integer
from app.database import Base


class PoolingUsers(Base):
    __tablename__ = 'pooling_users'
    pooling_id = Column(Integer, ForeignKey(
        'pooling.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='CASCADE'), primary_key=True)
