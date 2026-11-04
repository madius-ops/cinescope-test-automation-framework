import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()


class MoviesDbCreds:
    HOST = os.getenv('DB_MOVIES_HOST')
    PORT = os.getenv('DB_MOVIES_PORT')
    DATABASE_NAME = os.getenv('DB_MOVIES_NAME')
    USERNAME = os.getenv('DB_MOVIES_USERNAME')
    PASSWORD = os.getenv('DB_MOVIES_PASSWORD')