from pydantic import BaseModel, EmailStr, Field, fields, validator
from typing import Optional
from datetime import datetime
from app.enums import Gender, City, CodeStatus


class OurBaseModel(BaseModel):
    class Config:
        orm_mode = True


class Car(OurBaseModel):
    car_name: str = Field(min_length=2)
    car_type: str = Field(min_length=4)
    description: str = Field(min_length=4)


class EditCar(OurBaseModel):
    car_name: Optional[str] = Field(min_length=2)
    car_type: Optional[str] = Field(min_length=4)
    description: Optional[str] = Field(min_length=4)


class CarOut(OurBaseModel):
    car_name: Optional[str] = None
    car_type: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None
    message: Optional[str] = None
    status: Optional[int] = None


class CarsOut(OurBaseModel):
    car_list: Optional[list[CarOut]] = []
    message: Optional[str] = None
    status: Optional[int] = None


class User(OurBaseModel):
    cin: str = Field(max_length=8, min_length=8)
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    password: str = Field(min_length=6)
    confirmed_password: str = Field(min_length=6)
    email: EmailStr
    age: int = Field(gt=13)
    gender: Gender


class EditUser(OurBaseModel):
    first_name: Optional[str] = Field(None, min_length=3)
    last_name: Optional[str] = Field(None, min_length=3)
    email: Optional[EmailStr] = Field(None)
    cin: Optional[str] = Field(None, min_length=8, max_length=8)
    age: Optional[int] = Field(None, gt=13)
    active: Optional[bool]
    confirmed: Optional[bool]


class UserOut(OurBaseModel):
    id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    active: Optional[bool] = None
    confirmed: Optional[bool] = None
    created_on: Optional[datetime] = None
    message: Optional[str] = None
    status: Optional[int] = None


class UserDelete(OurBaseModel):
    password: str = Field(min_length=6)
    confirmed_password: str = Field(max_length=6)


class UserLogin(OurBaseModel):
    email: EmailStr
    password: str


class Pool(OurBaseModel):
    description: str
    date_depart: datetime = None
    available_seats: int = Field(gt=0, lt=5)
    beg_dest: City
    end_dest: City
    price: float
    car_id: int

    @validator('date_depart')
    def validate_date_depart(cls, value):
        if value and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value


class PoolOut(OurBaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    date_depart: Optional[datetime] = None
    available_seats: Optional[int] = None
    beg_dest: Optional[City] = None
    end_dest: Optional[City] = None
    price: Optional[float] = None
    driver_id: Optional[int] = None
    car_id: Optional[int] = None
    message: Optional[str] = None
    status: Optional[int] = None


class PoolsOut(OurBaseModel):
    pool_list: Optional[list[PoolOut]] = []
    message: Optional[str] = None
    status: Optional[int] = None


class Pooling(OurBaseModel):

    description: Optional[str] = None
    date_depart: Optional[datetime] = None
    available_seats: Optional[int] = None
    beg_dest: Optional[City] = None
    end_dest: Optional[City] = None
    price: Optional[float] = None
    driver_first_name: Optional[str] = None
    driver_last_name: Optional[str] = None
    car_name: Optional[str] = None


class PoolingOut(OurBaseModel):
    pooling_list: Optional[list[Pooling]] = []
    message: Optional[str] = None
    status: Optional[int] = None


class ConfirmationCode(OurBaseModel):
    email: EmailStr
    confirmation_code: str
    status: CodeStatus


class ConfirmAccountOut(OurBaseModel):
    message: Optional[str] = None
    status: Optional[int] = None


class Token(OurBaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    message: Optional[str] = None
    status: Optional[int] = None


class UserConfirm(OurBaseModel):
    confirmed: bool


class ConfirmationCodeDeactivate(OurBaseModel):
    status: CodeStatus


class ConfirmAccount(OurBaseModel):
    confirmation_code: str


class ErrorOut(OurBaseModel):
    id: Optional[int] = None
    orig: Optional[str] = None
    statement: Optional[str] = None
    params: Optional[str] = None
    created_on: Optional[datetime] = None
    message: Optional[str] = None
    status: Optional[int] = None


class TokenData(OurBaseModel):
    id: Optional[str] = None


class ForgotPassword(OurBaseModel):
    email: EmailStr


class ForgotPasswordOut(OurBaseModel):
    message: Optional[str] = None
    status: Optional[int] = None


class ResetPassword(OurBaseModel):
    reset_password_token: str
    new_password: str
    confirm_new_password: str


class ResetPasswordOut(OurBaseModel):
    message: Optional[str] = None
    status: Optional[int] = None


class UserResetPassword(OurBaseModel):
    email: EmailStr
    password: str


class ResetCodeDeactivate(OurBaseModel):
    status: CodeStatus
