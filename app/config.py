import os
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI

env_path = Path(__file__).resolve().parents[1] / '.env'
print(f".env !!!!!!!! {env_path}")

load_dotenv(dotenv_path=env_path)

# Email Configuration
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

# JWT Settings
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in the environment variables.")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
