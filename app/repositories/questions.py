from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from ..database.models import Question
from ..schemas.questions import QuestionCreate, QuestionUpdate

VALID_TYPES = ["multiple_choice", "true_false"]


class QuestionsRepository:
    def get_question_by_id(self, db: Session, question_id: int) -> Question:
        question = (
            db.query(Question).filter(Question.question_id == question_id).first()
        )
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return question

    def get_quiz_questions(self, db: Session, quiz_id: int) -> list[Question]:
        questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
        if not questions:
            raise HTTPException(
                status_code=404, detail="No questions found for the specified quiz"
            )
        return questions

    def create_question(
        self, db: Session, quiz_id: int, question_data: QuestionCreate
    ) -> Question:
        try:
            if question_data.question_type not in VALID_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid question type. Must be one of: {', '.join(VALID_TYPES)}",
                )

            new_question = Question(
                quiz_id=quiz_id,
                question_text=question_data.question_text,
                question_type=question_data.question_type,
                options=question_data.options,
                correct_answer=question_data.correct_answer,
            )
            db.add(new_question)
            db.commit()
            db.refresh(new_question)
            return new_question
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Integrity error while creating question: {str(e)}",
            )

    def update_question(
        self, db: Session, question_id: int, question_data: QuestionUpdate
    ) -> Question:
        question = self.get_question_by_id(db, question_id)
        try:
            if (
                question_data.question_type
                and question_data.question_type not in VALID_TYPES
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid question type. Must be one of: {', '.join(VALID_TYPES)}",
                )
            for field, value in question_data.dict(exclude_unset=True).items():
                setattr(question, field, value)
            db.commit()
            db.refresh(question)
            return question
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Integrity error while updating question: {str(e)}",
            )

    def delete_question(self, db: Session, question_id: int):
        question = self.get_question_by_id(db, question_id)
        try:
            db.delete(question)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Integrity error while deleting question: {str(e)}",
            )
