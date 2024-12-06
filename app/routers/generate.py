from sqlite3 import IntegrityError
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.schemas.lessons import LessonCreate
from app.schemas.quizzes import QuizCreate
from app.schemas.questions import QuestionCreate
from app.repositories.lessons import LessonsRepository
from app.repositories.quizzes import QuizzesRepository
from app.repositories.questions import QuestionsRepository
from app.repositories.users import UsersRepository
from app.utils.security import decode_jwt_token
from app.utils.lesson_generator import create_lesson
from app.database.base import get_db, SessionLocal
import json
from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging



router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")

# Initialize ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

users_repository = UsersRepository()
lessons_repository = LessonsRepository()
quizzes_repository = QuizzesRepository()
questions_repository = QuestionsRepository()

@router.post("/generate")
async def generate_lessons(
     learning_field: str, description: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Endpoint to generate lessons, quizzes, and questions based on the learning field and description.
    The generation runs in the background to improve response time.
    """
    user_id = decode_jwt_token(token)
    # Input Validation
    if not description.strip():
        raise HTTPException(status_code=400, detail="Description cannot be empty")

    if not learning_field.strip():
        raise HTTPException(status_code=400, detail="Learning field cannot be empty")

    # Schedule background task
    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        executor, generate_lesson_background, user_id, learning_field, description
    )

    return {"status": "processing"}


def generate_lesson_background(user_id: int, learning_field: str, description: str):
    """
    Background task to generate a single lesson, quiz, and questions, and populate the database.
    """
    db = SessionLocal()
    try:
        # Generate lesson JSON
        lesson_JSON = create_lesson(learning_field, description)
        lesson_data = json.loads(lesson_JSON)

        logger.info(f"Generated lesson data: {json.dumps(lesson_data, indent=4)}")
        create_lesson_from_json(lesson_data, db, user_id)

    except json.JSONDecodeError:
        logger.error("Failed to parse the generated lesson JSON.")
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error while creating lesson: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"An unexpected error occurred: {str(e)}")
    finally:
        db.close()


def create_lesson_from_json(json_data, db: Session, user_id: int):
    """
    Populate a single lesson, quiz, and questions in the database using the JSON structure.
    """
    try:
        lesson_data_obj = LessonCreate(
            title=json_data.get("title", "Untitled Lesson"),
            description=json_data.get("description", ""),
            content=json_data.get("content", []),
        )

        lesson = lessons_repository.create_lesson(
            db=db, user_id=user_id, lesson_data=lesson_data_obj
        )

        quiz_data = json_data.get("quiz", {})
        if quiz_data:
            quiz_data_obj = QuizCreate(
                title=quiz_data.get("title", "Untitled Quiz"),
                description=quiz_data.get("description", ""),
            )

            quiz = quizzes_repository.create_quiz(
                db=db, lesson_id=lesson.lesson_id, quiz_data=quiz_data_obj
            )

            questions = quiz_data.get("questions", [])
            for question_data in questions:
                question_data_obj = QuestionCreate(
                    question_text=question_data.get("question_text", ""),
                    question_type=question_data.get("question_type", ""),
                    options=question_data.get("options", []),
                    correct_answer=question_data.get("correct_answer", ""),
                )

                questions_repository.create_question(
                    db=db, quiz_id=quiz.quiz_id, question_data=question_data_obj
                )

        db.commit()
        logger.info("Lesson, quiz, and questions created successfully.")
        return {"detail": "Lesson created successfully"}

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail=f"Integrity error while creating lesson: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
