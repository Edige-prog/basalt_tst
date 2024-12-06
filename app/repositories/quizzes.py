from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from ..database.models import Quiz
from ..schemas.quizzes import QuizCreate, QuizUpdate


class QuizzesRepository:
    def get_quiz_by_id(self, db: Session, quiz_id: int) -> Quiz:
        quiz = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        return quiz

    def get_lesson_quiz(self, db: Session, lesson_id: int) -> Quiz:
        quiz = db.query(Quiz).filter(Quiz.lesson_id == lesson_id).first()
        if not quiz:
            raise HTTPException(
                status_code=404, detail="No quiz found for the specified lesson"
            )
        return quiz

    def create_quiz(self, db: Session, lesson_id: int, quiz_data: QuizCreate) -> Quiz:
        try:
            # Ensure no duplicate quiz for the lesson
            existing_quiz = db.query(Quiz).filter(Quiz.lesson_id == lesson_id).first()
            if existing_quiz:
                raise HTTPException(
                    status_code=400,
                    detail="A quiz already exists for this lesson",
                )

            new_quiz = Quiz(
                lesson_id=lesson_id,
                title=quiz_data.title,
                description=quiz_data.description,
            )
            db.add(new_quiz)
            db.commit()
            db.refresh(new_quiz)
            return new_quiz
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=400, detail=f"Integrity error while creating quiz: {str(e)}"
            )

    def update_quiz(self, db: Session, quiz_id: int, quiz_data: QuizUpdate) -> Quiz:
        quiz = self.get_quiz_by_id(db, quiz_id)
        try:
            for field, value in quiz_data.dict(exclude_unset=True).items():
                setattr(quiz, field, value)
            db.commit()
            db.refresh(quiz)
            return quiz
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=400, detail=f"Integrity error while updating quiz: {str(e)}"
            )

    def delete_quiz(self, db: Session, quiz_id: int):
        quiz = self.get_quiz_by_id(db, quiz_id)
        try:
            db.delete(quiz)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=400, detail=f"Integrity error while deleting quiz: {str(e)}"
            )
