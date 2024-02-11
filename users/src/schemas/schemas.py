from typing import Union
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: Union[str, None] = None
    password: Union[str, None] = None
    email: Union[str, None] = None
    dni: Union[str, None] = None
    fullName: Union[str, None] = None
    phoneNumber: Union[str, None] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    status: Union[str, None] = None
    dni: Union[str, None] = None
    fullName: Union[str, None] = None
    phoneNumber: Union[str, None] = None

    class Config:
        from_attributes = True


class generateToken(BaseModel):
    username: Union[str, None] = None
    password: Union[str, None] = None

    class Config:
        from_attributes = True
