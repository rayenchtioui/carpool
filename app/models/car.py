import datetime
from sqlalchemy import Date,Boolean, Column, ForeignKey, Integer, String,DateTime,Enum,Float
from sqlalchemy.orm import relationship

from app.database import Base
from app.enums import *

class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True,nullable=False)
    car_name = Column(String, nullable=False)
    car_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id",ondelete = 'CASCADE'))
    pooling = relationship('Pooling',backref='cars')