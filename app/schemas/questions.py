from typing import List, Optional
from pydantic import BaseModel


class QuestionBase(BaseModel):
    question_text: str
    question_type: str  # "multiple_choice" or "true_false"
    options: Optional[List[str]] = None  # Only for multiple-choice
    correct_answer: str


class QuestionCreate(QuestionBase):
    """
    Schema for creating a question.
    """

    class Config:
        schema_extra = {
            "example": {
                "question_text": "What does AI stand for?",
                "question_type": "multiple_choice",
                "options": [
                    "Artificial Intelligence",
                    "Animal Instinct",
                    "Applied Informatics",
                ],
                "correct_answer": "Artificial Intelligence",
            }
        }


class QuestionUpdate(BaseModel):
    """
    Schema for updating a question.
    """

    question_text: Optional[str] = None
    question_type: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "question_text": "Updated question text",
                "correct_answer": "Updated correct answer",
            }
        }


class QuestionResponse(QuestionBase):
    """
    Schema for the response object of a question.
    """

    question_id: int
    quiz_id: int

    class Config:
        orm_mode = True
