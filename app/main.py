import threading
import time

import requests
from app.routers.auth import router as auth_router
from app.routers.generate import router as generate_router
from app.routers.lessons import router as lessons_router
from app.routers.quizzes import router as quizzes_router
from app.routers.questions import router as questions_router


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(generate_router, prefix="/generate", tags=["generate"])
app.include_router(lessons_router, prefix="/lessons", tags=["lessons"])
app.include_router(quizzes_router, prefix="/quizzes", tags=["quizzes"])
app.include_router(questions_router, prefix="/questions", tags=["questions"])


@app.get("/")
def root():
    return {"message": "Service is running"}


@app.get("/healthcheck")
def health_check():
    return {"status": "ok"}


# ping
def send_ping():
    while True:
        try:
            response = requests.get("https://basalt-tst.onrender.com/docs")
            print(f"Ping status: {response.status_code}")
        except Exception as e:
            print(f"Failed to ping the server: {e}")
        time.sleep(600)  # Sleep 10 minutes


# Run ping thread
ping_thread = threading.Thread(target=send_ping)
ping_thread.daemon = True
ping_thread.start()
