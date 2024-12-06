from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    fullname: str
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "fullname": "John Doe",
                "email": "johndoe@example.com",
                "password": "password123",
            }
        }


class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None

    class Config:
        schema_extra = {
            "example": {
                "fullname": "John Doe Updated",
                "email": "updated_email@example.com",
            }
        }


class UserInfo(BaseModel):
    id: int
    fullname: str
    email: EmailStr

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "fullname": "John Doe",
                "email": "johndoe@example.com",
            }
        }


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True