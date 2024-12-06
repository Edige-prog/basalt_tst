from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.repositories.quizzes import QuizzesRepository
from app.repositories.questions import QuestionsRepository
from app.repositories.lessons import LessonsRepository
from app.schemas.quizzes import (
    QuizCreate,
    QuizUpdate,
    QuizResponse,
    QuizSubmission,
    QuizSubmissionResult,
)
from app.database.base import get_db
from app.utils.security import decode_jwt_token, ensure_user_owns_resource

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")

lessons_repository = LessonsRepository()
quizzes_repository = QuizzesRepository()
questions_repository = QuestionsRepository()


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
def get_quiz(
    quiz_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Retrieve a single quiz by ID.
    """
    user_id = decode_jwt_token(token)
    quiz = quizzes_repository.get_quiz_by_id(db, quiz_id)
    lesson = lessons_repository.get_lesson_by_id(db, quiz.lesson_id)
    ensure_user_owns_resource(lesson.user_id, user_id)
    return quiz


@router.get("/quizzes/lesson/{lesson_id}", response_model=QuizResponse)
def get_lesson_quiz(
    lesson_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Retrieve the quiz for a specific lesson.
    """
    user_id = decode_jwt_token(token)
    lesson = lessons_repository.get_lesson_by_id(db, lesson_id)
    ensure_user_owns_resource(lesson.user_id, user_id)
    return quizzes_repository.get_lesson_quiz(db, lesson_id)


@router.post("/quizzes", response_model=QuizResponse)
def create_quiz(
    lesson_id: int,
    quiz_data: QuizCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Create a new quiz for a lesson.
    """
    user_id = decode_jwt_token(token)
    lesson = lessons_repository.get_lesson_by_id(db, lesson_id)
    ensure_user_owns_resource(lesson.user_id, user_id)
    return quizzes_repository.create_quiz(db, lesson_id, quiz_data)


@router.put("/quizzes/{quiz_id}", response_model=QuizResponse)
def update_quiz(
    quiz_id: int,
    quiz_data: QuizUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Update an existing quiz by ID.
    """
    user_id = decode_jwt_token(token)
    quiz = quizzes_repository.get_quiz_by_id(db, quiz_id)
    lesson = lessons_repository.get_lesson_by_id(db, quiz.lesson_id)
    ensure_user_owns_resource(lesson.user_id, user_id)
    return quizzes_repository.update_quiz(db, quiz_id, quiz_data)


@router.delete("/quizzes/{quiz_id}")
def delete_quiz(
    quiz_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Delete a quiz by ID.
    """
    user_id = decode_jwt_token(token)
    quiz = quizzes_repository.get_quiz_by_id(db, quiz_id)
    lesson = lessons_repository.get_lesson_by_id(db, quiz.lesson_id)
    ensure_user_owns_resource(lesson.user_id, user_id)
    quizzes_repository.delete_quiz(db, quiz_id)
    return {"detail": "Quiz deleted successfully"}


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizSubmissionResult)
def submit_quiz(
    quiz_id: int,
    submission: QuizSubmission,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Submit a quiz and evaluate the answers.
    Returns the number of correct answers and the correct answers for each question.
    """
    user_id = decode_jwt_token(token)

    quiz = quizzes_repository.get_quiz_by_id(db, quiz_id)

    lesson = lessons_repository.get_lesson_by_id(db, quiz.lesson_id)
    ensure_user_owns_resource(lesson.user_id, user_id)

    questions = questions_repository.get_quiz_questions(db, quiz_id)

    if not questions:
        raise HTTPException(status_code=400, detail="Quiz has no questions.")

    correct_count = 0
    correct_answers = {}

    for question in questions:
        user_answer = submission.answers.get((question.question_id))
        if user_answer is None:
            continue

        if (
            question.question_type == "multiple_choice"
            and user_answer == question.correct_answer
        ):
            correct_count += 1
        elif (
            question.question_type == "true_false"
            and user_answer.lower() == question.correct_answer.lower()
        ):
            correct_count += 1

        correct_answers[question.question_id] = question.correct_answer

    return QuizSubmissionResult(
        total_questions=len(questions),
        correct_count=correct_count,
        correct_answers=correct_answers,
    )
