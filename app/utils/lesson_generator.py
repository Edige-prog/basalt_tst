from ..config import client


def create_lesson(thing_to_learn, description):
    prompt = f"""
        You are an assistant that generates structured JSON responses for creating educational content. 
        The content should be focused on "{thing_to_learn}" with the following description: "{description}".
        The JSON structure should follow this hierarchy: Lessons -> Quizzes -> Questions.
        
        Please create a JSON response that adheres to the following requirements:
        - Include 1 lesson.
        - Each lesson should have 1 quiz.
        - Each quiz should contain 5 questions.

        The JSON response should have the following fields:
        - Lesson:
            - `title`: The title of the lesson. Make it short (2-3 words). Don't use the word "Lesson".
            - `description`: A brief description of the lesson.
            - `content`: A list of content objects (e.g., text). The content should be educational and detailed, teaching the student about the topic, followed by prompts to test their knowledge. Include 2-4 paragraphs of detailed text.
            - `quiz`: A single quiz object.
        - Quiz:
            - `title`: The title of the quiz. Make it short (2-3 words). Don't use the word "Quiz".
            - `description`: A brief description of the quiz.
            - `questions`: A list of question objects.
        - Question:
            - `question_text`: The text of the question.
            - `question_type`: The type of the question, either "multiple_choice" or "true_false".
            - `options`: If it is a multiple-choice question, provide a list of options.
            - `correct_answer`: The correct answer for the question.

        Example JSON structure (simplified):

            {{
                "title": "Lesson Title 1",
                "description": "Description of Lesson 1",
                "content": [
                    {{"type": "text", "value": "Educational content here."}},
                    {{"type": "text", "value": "Additional content here."}}
                ],
                "quiz": {{
                    "title": "Quiz Title 1",
                    "description": "Description of Quiz 1",
                    "questions": [
                        {{
                            "question_text": "What is the capital of France?",
                            "question_type": "multiple_choice",
                            "options": ["Paris", "London", "Berlin", "Madrid"],
                            "correct_answer": "Paris"
                        }},
                        {{
                            "question_text": "Is the Earth round?",
                            "question_type": "true_false",
                            "correct_answer": "true"
                        }}
                    ]
                }}
            }}

        Please generate a fully detailed JSON response according to the given specifications. Only return the JSON response. Do not include any additional text. Do not include any tags like json before JSON itself PURE JSON.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that provides JSON responses.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content