from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from ..database.models import Lesson
from ..schemas.lessons import LessonCreate, LessonUpdate
from typing import Optional
import asyncio
import uuid
from ..utils.tts import extract_text_from_content, generate_and_save_audio


class LessonsRepository:
    def get_lesson_by_id(self, db: Session, lesson_id: int) -> Lesson:
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        return lesson

    def get_user_lessons(self, db: Session, user_id: int) -> list[Lesson]:
        lessons = db.query(Lesson).filter(Lesson.user_id == user_id).all()
        if not lessons:
            raise HTTPException(status_code=404, detail="No lessons found for the user")
        return lessons

    # def create_lesson(
    #     self, db: Session, user_id: int, lesson_data: LessonCreate
    # ) -> Lesson:
    #     try:
    #         new_lesson = Lesson(
    #             user_id=user_id,
    #             title=lesson_data.title,
    #             description=lesson_data.description,
    #             content=lesson_data.content,
    #         )
    #         db.add(new_lesson)
    #         db.commit()
    #         db.refresh(new_lesson)
    #         return new_lesson
    #     except IntegrityError as e:
    #         db.rollback()
    #         raise HTTPException(
    #             status_code=400,
    #             detail=f"Integrity error while creating lesson: {str(e)}",
    #         )

    def create_lesson(
        self, db: Session, user_id: int, lesson_data: LessonCreate
    ) -> Lesson:
        try:
            # Create a new lesson object
            new_lesson = Lesson(
                user_id=user_id,
                title=lesson_data.title,
                description=lesson_data.description,
                content=lesson_data.content,
            )
            db.add(new_lesson)
            db.commit()
            db.refresh(new_lesson)

            # Generate audio if content exists
            if new_lesson.content:
                text = extract_text_from_content(new_lesson.content)
                if text:
                    filename = (
                        f"lesson_{new_lesson.lesson_id}_{uuid.uuid4().hex[:8]}.mp3"
                    )
                    # Call the audio generator (using asyncio to run it asynchronously)
                    audio_path = asyncio.run(
                        generate_and_save_audio(text, "en-US-GuyNeural", filename)
                    )
                    new_lesson.audio_file_path = str(audio_path)
                    db.commit()
                    db.refresh(new_lesson)

            return new_lesson
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Integrity error while creating lesson: {str(e)}",
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while creating lesson: {str(e)}",
            )

    def update_lesson(
        self, db: Session, lesson_id: int, lesson_data: LessonUpdate
    ) -> Lesson:
        lesson = self.get_lesson_by_id(db, lesson_id)
        try:
            for field, value in lesson_data.dict(exclude_unset=True).items():
                setattr(lesson, field, value)
            db.commit()
            db.refresh(lesson)
            return lesson
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Integrity error while updating lesson: {str(e)}",
            )

    def delete_lesson(self, db: Session, lesson_id: int):
        lesson = self.get_lesson_by_id(db, lesson_id)
        try:
            db.delete(lesson)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Integrity error while deleting lesson: {str(e)}",
            )

