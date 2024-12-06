from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.repositories.lessons import LessonsRepository
from app.schemas.lessons import LessonCreate, LessonUpdate, LessonResponse
from app.database.base import get_db
from app.utils.security import decode_jwt_token
import os

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")
lessons_repository = LessonsRepository()

@router.get("/lessons", response_model=list[LessonResponse])
def get_user_lessons(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get all lessons for the current user.
    """
    user_id = decode_jwt_token(token)
    return lessons_repository.get_user_lessons(db, user_id)


@router.post("/lessons", response_model=LessonResponse)
def create_lesson(
    lesson_data: LessonCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Create a new lesson for the current user.
    """
    user_id = decode_jwt_token(token)
    return lessons_repository.create_lesson(db, user_id, lesson_data)


@router.put("/lessons/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: int,
    lesson_data: LessonUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Update a lesson by ID for the current user.
    """
    user_id = decode_jwt_token(token)
    lesson = lessons_repository.get_lesson_by_id(db, lesson_id)
    if lesson.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this lesson")
    return lessons_repository.update_lesson(db, lesson_id, lesson_data)


@router.delete("/lessons/{lesson_id}")
def delete_lesson(lesson_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Delete a lesson by ID for the current user.
    """
    user_id = decode_jwt_token(token)
    lesson = lessons_repository.get_lesson_by_id(db, lesson_id)
    if lesson.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this lesson")
    lessons_repository.delete_lesson(db, lesson_id)
    return {"detail": "Lesson deleted successfully"}

@router.get("/lessons/{lesson_id}/audio", response_class=FileResponse)
def get_audio_for_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve the audio file for the specified lesson.
    """
    # Use the correct method to fetch the lesson
    lesson = lessons_repository.get_lesson_by_id(db, lesson_id)

    if not lesson.audio_file_path or not os.path.exists(lesson.audio_file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=lesson.audio_file_path,
        media_type="audio/mpeg",
        filename=os.path.basename(lesson.audio_file_path),
    )