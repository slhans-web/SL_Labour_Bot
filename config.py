import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Google Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# SQLite Database File Path
DB_FILE = "labor_data.db"
