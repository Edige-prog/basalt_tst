from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict

class VerificationCodeCreate(BaseModel):
    email: EmailStr
    purpose: str  # 'registration', 'login', or 'password_reset'

    class Config:
        schema_extra = {
            "example": {
                "email": "johndoe@example.com",
                "purpose": "registration",
            }
        }


class VerificationCodeVerify(BaseModel):
    email: EmailStr
    code: str

    class Config:
        schema_extra = {
            "example": {
                "email": "johndoe@example.com",
                "code": "123456",
            }
        }


class UserRegistrationData(BaseModel):
    email: EmailStr
    code: str
    fullname: str
    password: str

    class Config:
        orm_mode = True


class PasswordResetInitiate(BaseModel):
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=4)

    model_config = ConfigDict(from_attributes=True)