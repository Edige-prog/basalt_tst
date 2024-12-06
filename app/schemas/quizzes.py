from typing import Optional, Dict
from pydantic import BaseModel, Field


class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None


class QuizCreate(QuizBase):
    """
    Schema for creating a quiz.
    """

    class Config:
        schema_extra = {
            "example": {
                "title": "AI Basics Quiz",
                "description": "Test your knowledge of AI basics.",
            }
        }


class QuizUpdate(BaseModel):
    """
    Schema for updating a quiz.
    """

    title: Optional[str] = None
    description: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "title": "Updated Quiz Title",
                "description": "Updated description of the quiz.",
            }
        }


class QuizResponse(QuizBase):
    """
    Schema for the response object of a quiz.
    """

    quiz_id: int
    lesson_id: int

    class Config:
        orm_mode = True


class QuizSubmission(BaseModel):
    """
    Schema for submitting quiz answers.
    `answers` is a dictionary where keys are question IDs and values are user-submitted answers.
    """

    # answers: Dict[str, str]  # [question_id, answer]
    answers: Dict[int, str] = Field(
        ...,
        example={
            1: "Robert Griesemer, Rob Pike, and Ken Thompson",
            2: "false",
            3: ".go",
            4: "Reads an input from the user",
            5: "false",
        },
    )


class QuizSubmissionResult(BaseModel):
    """
    Schema for the result of a quiz submission.
    """

    total_questions: int
    correct_count: int
    correct_answers: Dict[int, str] = Field(
        ...,
        example={
            1: "Robert Griesemer, Rob Pike, and Ken Thompson",
            2: "false",
            3: ".go",
            4: "Prints a line to the console",
            5: "false",
        },
    )
