from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum, Float
from sqlalchemy.orm import relationship

from app.database import Base
from app.enums import *


class PoolingHisotry(Base):
    __tablename__ = 'pooling_history'
    id = Column(Integer, primary_key=True, nullable=False)
    description = Column(String, nullable=False)
    date_depart = Column(DateTime, nullable=False)
    available_seats = Column(Integer, nullable=False)
    availability = Column(Boolean, nullable=False, default=True)
    beg_dest = Column(Enum(City), nullable=False)
    end_dest = Column(Enum(City), nullable=False)
    price = Column(Float, nullable=False)
    driver_id = Column(Integer, nullable=False)
    car_id = Column(Integer, nullable=False)
