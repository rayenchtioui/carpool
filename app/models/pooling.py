import datetime
from sqlalchemy import Date,Boolean, Column, ForeignKey, Integer, String,DateTime,Enum,Float
from sqlalchemy.orm import relationship

from app.database import Base
from app.enums import *

class Pooling(Base):
    __tablename__ = 'pooling'
    id = Column(Integer, primary_key=True,nullable=False)
    description = Column(String,nullable=False)
    date_depart = Column(DateTime, nullable=False)
    available_seats = Column(Integer,nullable=False)
    beg_dest= Column(Enum(City), nullable=False)
    end_dest = Column(Enum(City), nullable=False)
    price = Column(Float,nullable=False)
    driver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    passanger_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
