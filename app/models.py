import datetime
from sqlalchemy import Date,Boolean, Column, ForeignKey, Integer, String,DateTime,Enum,Float
from sqlalchemy.orm import relationship

from app.database import Base
from app.enums import *

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True,nullable=False)
    cin = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    age = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    active = Column(Boolean, nullable = False, default = True)
    confirmed = Column(Boolean, nullable = False, default = False)
    created_on = Column(DateTime, default = datetime.datetime.utcnow())
    cars = relationship('Car',backref='users')
    pooling = relationship('Pooling',backref='users')

class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True,nullable=False)
    car_name = Column(String, nullable=False)
    car_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id",ondelete = 'CASCADE'))
    pooling = relationship('Pooling',backref='cars')

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
