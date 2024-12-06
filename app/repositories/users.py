from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database.models import User, VerificationCode
from ..schemas.users import UserCreate, UserUpdate
from ..schemas.verification_code import VerificationCodeCreate
from ..utils.code_generator import generate_verification_code


class UsersRepository:
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Create a new user."""
        try:
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="User with this email already exists")

            new_user = User(
                fullname=user_data.fullname,
                email=user_data.email,
                password_hashed=user_data.password
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Integrity error occurred while creating the user.")

    def get_user_by_email(self, db: Session, email: str) -> User:
        """Retrieve a user by their email."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    def get_user_by_email_reg(self, db: Session, email: str) -> User:
        """Get user by email (for registration purposes)"""
        user = db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, db: Session, user_id: int) -> User:
        """Retrieve a user by their ID."""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def update_user(self, db: Session, user_id: int, user_data: UserUpdate):
        """Update a user."""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Dynamically update fields
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)

        try:
            db.commit()
            db.refresh(user)
            return user

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Integrity error occurred while updating the user.")

    def delete_user(self, db: Session, user_id: int):
        """Delete a user by their ID."""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()

    def create_verification_code(self, db: Session, verification_data: VerificationCodeCreate) -> VerificationCode:
        """Generate a verification code for the user."""
        code = generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        verification_code = VerificationCode(
            email=verification_data.email,
            code=code,
            purpose=verification_data.purpose,
            expires_at=expires_at
        )
        db.add(verification_code)
        db.commit()
        db.refresh(verification_code)
        return verification_code

    def verify_code(self, db: Session, email: str, code: str, purpose: str) -> bool:
        """Verify a given verification code."""
        verification_entry = db.query(VerificationCode).filter(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.purpose == purpose,
            VerificationCode.expires_at >= datetime.utcnow()
        ).first()

        if verification_entry:
            # Delete the code after successful verification
            db.delete(verification_entry)
            db.commit()
            return True
        return False