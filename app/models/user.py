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