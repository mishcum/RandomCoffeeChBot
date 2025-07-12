from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')          

class Settings:
    BOT_TOKEN: str = os.getenv('BOT_TOKEN')
    DB_URL: str = os.getenv('DB_URL')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'DEBUG')

    class Config: 
        env_file = '.env'

@lru_cache
def get_settings() -> Settings:
    return Settings()
