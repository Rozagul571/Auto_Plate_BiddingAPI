# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    is_staff: bool = False

class User(UserBase):
    id: int
    is_staff: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str
# # app/schemas/user.py
# from pydantic import BaseModel, EmailStr
#
# class UserBase(BaseModel):
#     username: str
#     email: EmailStr
#
# class UserCreate(UserBase):
#     password: str
#     is_staff: bool = False  # Yangi field: is_staff, default False
#
# class User(UserBase):
#     id: int
#     is_staff: bool
#
#     class Config:
#         orm_mode = True
#
# class Token(BaseModel):
#     access_token: str
#     token_type: str