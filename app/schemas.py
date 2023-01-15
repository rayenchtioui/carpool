from pydantic import BaseModel, EmailStr, Field, fields, validator, root_validator
from typing import Optional
from datetime import datetime, timezone, timedelta
from app.enums import Gender, City, CodeStatus


class OurBaseModel(BaseModel):
    class Config:
        orm_mode = True

class Logout(OurBaseModel):
    message: Optional[str] = None
    status_code: Optional[int] = None

class Review(OurBaseModel):
    description: str = Field(min_length=6)
    stars: int = Field(gt=-1, lt=6)
    user_id: int


class ReviewOut(OurBaseModel):
    description: Optional[str]
    stars: Optional[int]
    user_id: Optional[int]
    reviewer_id: Optional[int]
    message: Optional[str] = None
    status: Optional[int] = None


class ReviewsOut(OurBaseModel):
    review_list: Optional[list[ReviewOut]] = []
    message: Optional[str] = None
    status: Optional[int] = None


class EditReview(OurBaseModel):
    description: Optional[str] = Field(min_length=6)
    stars: Optional[int] = Field(gt=-1, lt=6)


class Car(OurBaseModel):
    car_name: str = Field(min_length=2, example="BMW")
    car_type: str = Field(min_length=4, exmaple="luxe")
    description: str = Field(min_length=4, exmaple="very comfortable")


class EditCar(OurBaseModel):
    car_name: Optional[str] = Field(min_length=2, example="Mercedes")
    car_type: Optional[str] = Field(min_length=4, example="luxe")
    description: Optional[str] = Field(
        min_length=4, example="very comfortable")


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


def validate_age(dt: datetime):
    sixteen_years_ago = datetime.now() - timedelta(days=365 * 16)
    onehundred_years_ago = datetime.now() - timedelta(days=365 * 100)
    return dt > sixteen_years_ago and dt < onehundred_years_ago


class User(OurBaseModel):
    cin: str = Field(regex='^[0-9]{8}$', example='12345678')
    first_name: str = Field(min_length=3, regex='^[a-zA-Z ]*$', example='flen')
    last_name: str = Field(
        min_length=3, regex='^[a-zA-Z ]*$', example='ben foulen')
    password: str = Field(min_length=6, example='password')
    confirmed_password: str = Field(min_length=6, example='password')
    email: EmailStr
    age: datetime = Field(validator=validate_age,
                          example='2000-01-01T00:00:00Z')
    phone: str = Field(regex='^[0-9]{8}$', exmaple='99222333')
    gender: Gender


class EditUser(OurBaseModel):
    first_name: Optional[str] = Field(
        min_length=3, regex='^[a-zA-Z ]*$', example='flen')
    last_name: Optional[str] = Field(
        min_length=3, regex='^[a-zA-Z ]*$', example='ben foulen')
    cin: Optional[str] = Field(regex='^[0-9]{8}$', example='12345678')
    email: Optional[EmailStr]
    age: Optional[datetime] = Field(
        validator=validate_age, example='2000-01-01T00:00:00Z')
    phone: Optional[str] = Field(regex='^[0-9]{8}$', exmaple='99222333')


class UserOut(OurBaseModel):
    id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[datetime] = None
    phone: Optional[str] = None
    gender: Optional[Gender] = None
    active: Optional[bool] = None
    confirmed: Optional[bool] = None
    created_on: Optional[datetime] = None
    message: Optional[str] = None
    status: Optional[int] = None


class UsersOut(OurBaseModel):
    users_list: Optional[list[UserOut]] = []
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
    price: float = Field(exmaple='34')
    car_id: int

    @validator('date_depart')
    def validate_date_depart(cls, value):
        if value and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        if value and value < datetime.utcnow().replace(tzinfo=timezone.utc):
            raise ValueError("date_depart must not be in the past")
        return value

    @root_validator()
    def validate_beg_dest_and_end_dest(cls, values):
        if values.get('beg_dest') == values.get('end_dest'):
            raise ValueError(
                "beg_dest and end_dest must not have the same value")
        return values


class EditPool(Pool):
    description: Optional[str]
    date_depart: Optional[datetime]
    available_seats: Optional[int] = Field(gt=0, lt=5)
    availability: Optional[bool]
    beg_dest: Optional[City]
    end_dest: Optional[City]
    price: Optional[float]
    car_id: Optional[int]


class PoolOut(OurBaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    date_depart: Optional[datetime] = None
    available_seats: Optional[int] = None
    availability: Optional[bool]
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
    availability: Optional[bool]
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


class PoolUser(OurBaseModel):
    pooling_id: int
    user_id: int


class PoolUserOut(OurBaseModel):
    pooling_id: Optional[int] = None
    user_id: Optional[int] = None
    message: Optional[str] = None
    status: Optional[int] = None


class PoolingUserOut(OurBaseModel):
    pooling_id: Optional[int] = None
    user_id: Optional[int] = None
    driver_name: Optional[str] = None
    driver_last_name: Optional[str] = None
    driver_phone: Optional[str] = None
    car_name: Optional[str] = None
    price: Optional[int] = None


class PoolsUserOut(OurBaseModel):
    pooling_list: Optional[list[PoolingUserOut]] = []
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
