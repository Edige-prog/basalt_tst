- video demonstration: https://drive.google.com/file/d/1HWKsy8HBT9FhZYVGBuIhp3AnNhtWNRFH/view?usp=sharing

- linkto deployed website: https://basalt-tst.onrender.com/

- link to deployed documentation: https://basalt-tst.onrender.com/docs/

# **Project Overview**
Basalt is a platform for creating structured educational content, including lessons, quizzes, and questions. It features two-factor registration for secure user onboarding, password reset functionality, dynamic lesson generation, and text-to-speech (TTS) capabilities.

## **Features**

- ### **User Authentication and Authorization** ###:
- Two-Factor Registration: Users register with email verification to ensure secure account creation.*
- Password Reset: Users can initiate a password reset process via email.*
- User Authentication: Secure login and authentication using OAuth2 and JWT tokens.*
  
- ### **Lesson Management** ###: 
- Create Lessons: Dynamically generate lessons with text and quizzes.
- Manage Lessons: Update or delete lessons created by the user.
- Lesson Audio: Automatically generate audio files for lessons using TTS.

- ### **Quiz and Question Management** ###:
- Quizzes: Create, retrieve, update, and delete quizzes for lessons.
- Questions: Add, edit, and delete questions in quizzes.
- Submit Quiz: Evaluate quiz submissions and provide a summary of correct answers.

## **Technology Stack**

- **FastAPI**: High-performance web framework for building APIs.
- **SQLAlchemy**: SQL toolkit and ORM library for database management.
- **Alembic**: Database migration tool integrated with SQLAlchemy.
- **Edge-TTS**: Text-to-speech integration for audio generation.
- **SQLite**: Lightweight relational database for development.


## **Structure**
```
├── README.md
├── alembic
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       ├── 71cdd40d5af2_audio.py
│       └── fcf1cfbd25cf_fist_migration.py
├── alembic.ini
├── app
│   ├── config.py
│   ├── database
│   │   ├── base.py
│   │   └── models.py
│   ├── main.py
│   ├── repositories
│   │   ├── lessons.py
│   │   ├── questions.py
│   │   ├── quizzes.py
│   │   └── users.py
│   ├── routers
│   │   ├── auth.py
│   │   ├── generate.py
│   │   ├── lessons.py
│   │   ├── questions.py
│   │   └── quizzes.py
│   ├── schemas
│   │   ├── lessons.py
│   │   ├── questions.py
│   │   ├── quizzes.py
│   │   ├── users.py
│   │   └── verification_code.py
│   └── utils
│       ├── code_generator.py
│       ├── email_utils.py
│       ├── lesson_generator.py
│       ├── security.py
│       └── tts.py
├── requirements.txt
└── sql_app.db

9 directories, 32 files
```


## **Installation**

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/dimalbek/basalt_tst.git
    cd basalt_tst
    ```

2. **Set up a Virtual Environment (optional but recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```


4. **Create .env File in the root directory and fill it with the following content**:
    ```
    # Email Configuration
    MAIL_USERNAME=your_email@example.com
    MAIL_PASSWORD=your_email_password

    # JWT Settings
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=60
    SECRET_KEY=your_secret_key

    # API Keys
    OPENAI_API_KEY=your_openai_api_key
    ```

5. **Initialize the Database**:
    ```bash
    alembic upgrade head
    ```

6. **Run the Application**:
    ```bash
    uvicorn app.main:app --reload
    ```

The API will now be accessible at http://127.0.0.1:8000 .
You may check endpoints at http://127.0.0.1:8000/docs .

## **API Endpoints**
### User Authentication ###

- POST /auth/users/register/initiate: Initiate user registration with email verification.
- POST /auth/users/register/confirm: Complete registration by verifying the email.
- POST /auth/users/login: Log in with email and password to obtain a JWT token.
- POST /auth/users/password-reset/initiate: Start the password reset process by sending a verification code to the email.
- POST /auth/users/password-reset/confirm: Complete password reset using the verification code.

### Lesson Management ###

- POST /lessons: Create a new lesson for the current user.
- GET /lessons: Retrieve all lessons for the current user.
- GET /lessons/{lesson_id}: Retrieve a specific lesson by ID.
- PUT /lessons/{lesson_id}: Update a specific lesson by ID.
- DELETE /lessons/{lesson_id}: Delete a specific lesson by ID.
- GET /lessons/{lesson_id}/audio: Retrieve the audio file for a lesson.

### Quiz Management ###

- POST /quizzes: Create a new quiz for a lesson.
- GET /quizzes/{quiz_id}: Retrieve a specific quiz by ID.
- PUT /quizzes/{quiz_id}: Update a specific quiz by ID.
- DELETE /quizzes/{quiz_id}: Delete a specific quiz by ID.
- POST /quizzes/{quiz_id}/submit: Submit answers for a quiz and evaluate results.

### Question Management ###

- POST /questions: Add a new question to a quiz.
- GET /questions/{question_id}: Retrieve a specific question by ID.
- PUT /questions/{question_id}: Update a specific question by ID.
- DELETE /questions/{question_id}: Delete a specific question by ID.

## Author ##
Developed by Dinmukhamed Albek.
