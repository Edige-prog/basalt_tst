import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Response,
    HTTPException,
    Form,
    status,
    BackgroundTasks,
)
from fastapi.responses import JSONResponse
from jose import jwt
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr

from ..repositories.users import UsersRepository
from ..schemas.verification_code import PasswordResetInitiate, PasswordResetConfirm
from ..schemas.users import UserCreate, UserLogin, UserUpdate, UserInfo
from ..database.base import get_db
from ..utils.security import (
    hash_password,
    verify_password,
    create_jwt_token,
    decode_jwt_token,
)

from ..schemas.verification_code import (
    VerificationCodeCreate,
    VerificationCodeVerify,
    UserRegistrationData,
)
from ..utils.email_utils import send_email
from app.config import (
    MAIL_USERNAME,
    MAIL_PASSWORD,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


router = APIRouter()
users_repository = UsersRepository()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")


# Initiate Registration
@router.post("/users/register/initiate", status_code=200)
def initiate_registration(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    existing_user = users_repository.get_user_by_email_reg(db, email)
    if existing_user:
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )

    # Create a verification code
    verification_data = VerificationCodeCreate(email=email, purpose="registration")
    verification_code = users_repository.create_verification_code(db, verification_data)

    # Send verification email
    subject = "Your Registration Verification Code"
    body = f"Your verification code is: {verification_code.code}"
    background_tasks.add_task(send_email, email, subject, body)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Verification code sent to email."},
    )


# Confirm Registration
@router.post("/users/register/confirm", status_code=200)
def confirm_registration(
    user_input: UserRegistrationData, db: Session = Depends(get_db)
):
    # Verify code
    is_valid = users_repository.verify_code(
        db, user_input.email, user_input.code, "registration"
    )
    if not is_valid:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification code"
        )

    user_input.password = hash_password(user_input.password)

    new_user = users_repository.create_user(db, user_input)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Successfully registered.", "user_id": new_user.user_id},
    )


# Login endpoint
@router.post("/users/login")
def post_login(
    username: EmailStr = Form(), password: str = Form(), db: Session = Depends(get_db)
):
    user_data = UserLogin(email=username, password=password)
    user = users_repository.get_user_by_email(db, user_data.email)
    if not verify_password(password, user.password_hashed):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_jwt_token(user.user_id)
    return {"access_token": access_token, "token_type": "bearer"}


# Update user
@router.patch("/users/me")
def patch_user(
    user_input: UserUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = decode_jwt_token(token)
    updated_user = users_repository.update_user(db, user_id, user_input)
    serialized_user = {
        "id": updated_user.user_id,
        "fullname": updated_user.fullname,
        "email": updated_user.email,
    }
    return JSONResponse(
        content={"message": "User updated successfully", "user": serialized_user},
        status_code=200,
    )


# Get user info
@router.get("/users/me", response_model=UserInfo, status_code=200)
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    user_id = decode_jwt_token(token)
    user = users_repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return UserInfo(
        id=user.user_id,
        fullname=user.fullname,
        email=user.email,
    )

# Delete user
@router.delete("/users/me", status_code=200)
def delete_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Delete the current user's account.
    """
    # Decode the token to get the user's ID
    user_id = decode_jwt_token(token)

    # Call the repository to delete the user
    users_repository.delete_user(db, user_id)

    return JSONResponse(
        content={"message": "User account deleted successfully."},
        status_code=200,
    )

# Initiate Password Reset
@router.post("/users/password-reset/initiate", status_code=200)
async def initiate_password_reset(
    password_reset_initiate: PasswordResetInitiate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = users_repository.get_user_by_email(db, password_reset_initiate.email)
    if not user:
        raise HTTPException(
            status_code=404, detail="User with this email does not exist."
        )

    verification_data = VerificationCodeCreate(
        email=password_reset_initiate.email, purpose="password_reset"
    )
    verification_code = users_repository.create_verification_code(db, verification_data)

    subject = "Your Password Reset Verification Code"
    body = f"Your password reset verification code is: {verification_code.code}"
    background_tasks.add_task(send_email, password_reset_initiate.email, subject, body)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Password reset verification code sent to email."},
    )


# Confirm Password Reset
@router.post("/users/password-reset/confirm", status_code=200)
async def confirm_password_reset(
    password_reset_confirm: PasswordResetConfirm, db: Session = Depends(get_db)
):
    # Verify the code
    is_valid = users_repository.verify_code(
        db, password_reset_confirm.email, password_reset_confirm.code, "password_reset"
    )
    if not is_valid:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification code."
        )

    # Retrieve the user
    user = users_repository.get_user_by_email(db, password_reset_confirm.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Update the user's password
    user.password_hashed = hash_password(password_reset_confirm.new_password)
    db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Password has been reset successfully."},
    )
