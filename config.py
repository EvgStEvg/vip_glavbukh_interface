# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = "gpt-4"
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7
    SEARCH_CACHE_SIZE = 100
    HISTORY_LIMIT = 10
    REQUEST_TIMEOUT = 5
    N8N_WEBHOOK_URL = os.getenv ('N8N_WEBHOOK_URL')
    ENCRYPTION_KEY = os.getenv ('ENCRYPTION_KEY')
    # другие конфигурации