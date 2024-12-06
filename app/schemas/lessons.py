from typing import List, Optional
from pydantic import BaseModel


class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[List[dict]] = None


class LessonCreate(LessonBase):
    """
    Schema for creating a lesson.
    """

    class Config:
        schema_extra = {
            "example": {
                "title": "Introduction to AI",
                "description": "Learn the basics of artificial intelligence.",
                "content": [
                    {"type": "text", "value": "Artificial intelligence (AI) is..."},
                    {"type": "text", "value": "AI enables machines to learn..."},
                ],
            }
        }


class LessonUpdate(BaseModel):
    """
    Schema for updating a lesson.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[List[dict]] = None

    class Config:
        schema_extra = {
            "example": {
                "title": "Updated Lesson Title",
                "description": "Updated description of the lesson.",
            }
        }


class LessonResponse(LessonBase):
    """
    Schema for the response object of a lesson.
    """

    lesson_id: int
    user_id: int

    class Config:
        orm_mode = True
