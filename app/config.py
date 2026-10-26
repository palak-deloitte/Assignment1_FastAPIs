import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY")

MAX_TEXT_LENGTH = 5000   # characters; document this in the README
REQUEST_TIMEOUT = 5      # seconds for calls to weather/joke APIs