from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hashed = Column(String, nullable=False)

    lessons = relationship("Lesson", back_populates="user")
    verification_codes = relationship("VerificationCode", back_populates="user")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, fullname='{self.fullname}')>"


class Lesson(Base):
    __tablename__ = "lessons"

    lesson_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    position = Column(Integer, nullable=True)
    content = Column(JSON, nullable=True)
    audio_file_path = Column(String(255), nullable=True)

    user = relationship("User", back_populates="lessons")
    quiz = relationship("Quiz", back_populates="lesson", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lesson(lesson_id={self.lesson_id}, title='{self.title}')>"


class Quiz(Base):
    __tablename__ = "quizzes"

    quiz_id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.lesson_id"))
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    lesson = relationship("Lesson", back_populates="quiz")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quiz(quiz_id={self.quiz_id}, title='{self.title}')>"


class Question(Base):
    __tablename__ = "questions"

    question_id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.quiz_id"))
    question_text = Column(Text, nullable=False)
    question_type = Column(
        Enum("multiple_choice", "true_false", name="question_types"), nullable=False
    )
    options = Column(JSON)  # Available options for multiple-choice
    correct_answer = Column(String(255), nullable=False)

    quiz = relationship("Quiz", back_populates="questions")

    def __repr__(self):
        return f"<Question(question_id={self.question_id}, question_type='{self.question_type}')>"


class VerificationCode(Base):
    __tablename__ = "verification_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    email = Column(String, index=True, nullable=False)
    code = Column(String, nullable=False)
    purpose = Column(String, nullable=False)  # 'registration' or 'login' or 'reset'
    expires_at = Column(DateTime, nullable=False)
    
    user = relationship("User", back_populates="verification_codes")