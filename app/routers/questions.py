from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.repositories.questions import QuestionsRepository
from app.repositories.quizzes import QuizzesRepository
from app.repositories.lessons import LessonsRepository
from app.schemas.questions import QuestionCreate, QuestionUpdate, QuestionResponse
from app.database.base import get_db
from app.utils.security import decode_jwt_token, ensure_user_owns_resource

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")

questions_repository = QuestionsRepository()
quizzes_repository = QuizzesRepository()
lessons_repository = LessonsRepository()

@router.get("/questions/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieve a single question by ID.
    """
    user_id = decode_jwt_token(token)
    question = questions_repository.get_question_by_id(db, question_id)
    quiz = quizzes_repository.get_quiz_by_id(db, question.quiz_id)
    lesson = lessons_repository.get_lesson_by_id(db, quiz.lesson_id)
    ensure_user_owns_resource(lesson.user_id, user_id)
    return question


@router.get("/questions/quiz/{quiz_id}", response_model=list[QuestionResponse])
def get_quiz_questions(quiz_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieve all questions for a specific quiz.
    """
    user_id = decode_jwt_token(token)
    quiz = quizzes_repository.get_quiz_by_id(db, quiz_id)
    lesson = lessons_repository.get_lesson_by_id(db, quiz.lesson_id)
    ensure_user_owns_resource(lesson.user_id, user_id)
    return questions_repository.get_quiz_questions(db, quiz_id)


@router.post("/questions", response_model=QuestionResponse)
def create_question(
    quiz_id: int, question_data: QuestionCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Create a new question for a quiz.
    """
    user_id = decode_jwt_token(token)
    quiz = quizzes_repository.get_quiz_by_id(db, quiz_id)
    lesson = lessons_repository.get_lesson_by_id(db, quiz.lesson_id)
    ensure_user_owns_resource(lesson.user_id, user_id)
    return questions_repository.create_question(db, quiz_id, question_data)


@router.put("/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int, question_data: QuestionUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Update an existing question by ID.
    """
    user_id = decode_jwt_token(token)
    question = questions_repository.get_question_by_id(db, question_id)
    quiz = quizzes_repository.get_quiz_by_id(db, question.quiz_id)
    lesson = lessons_repository.get_lesson_by_id(db, quiz.lesson_id)
    ensure_user_owns_resource(lesson.user_id, user_id)
    return questions_repository.update_question(db, question_id, question_data)


@router.delete("/questions/{question_id}")
def delete_question(question_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Delete a question by ID.
    """
    user_id = decode_jwt_token(token)
    question = questions_repository.get_question_by_id(db, question_id)
    quiz = quizzes_repository.get_quiz_by_id(db, question.quiz_id)
    lesson = lessons_repository.get_lesson_by_id(db, quiz.lesson_id)
    ensure_user_owns_resource(lesson.user_id, user_id)
    questions_repository.delete_question(db, question_id)
    return {"detail": "Question deleted successfully"}