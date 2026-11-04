import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from resources.db_creds import MoviesDbCreds

USERNAME = MoviesDbCreds.USERNAME
PASSWORD = MoviesDbCreds.PASSWORD
HOST = MoviesDbCreds.HOST
PORT = MoviesDbCreds.PORT
DATABASE_NAME = MoviesDbCreds.DATABASE_NAME

#  движок для подключения к базе данных
engine = create_engine(
    f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}",
    echo=False  # Установить True для отладки SQL запросов
)

#  создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """Создает новую сессию БД"""
    return SessionLocal()


def connect_and_get_postgres_info():
    """Подключается к БД movies и выводит информацию о сервере PostgreSQL."""
    connection = None
    try:
        # Подключаемся к базе, используя креды из resources.db_creds
        connection = psycopg2.connect(
            host=MoviesDbCreds.HOST,
            port=MoviesDbCreds.PORT,
            database=MoviesDbCreds.DB_NAME,
            user=MoviesDbCreds.USER,
            password=MoviesDbCreds.PASSWORD,
        )

        cursor = connection.cursor()

        # Выполняем запрос на получение версии PostgreSQL
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()

        print(" Подключение к БД успешно установлено!")
        print(f"Информация о сервере: {db_version[0]}")

        cursor.close()

    except Exception as error:
        print(f" Ошибка при подключении к PostgreSQL: {error}")
        raise

    finally:
        if connection is not None:
            connection.close()
            print("Соединение с БД закрыто.")


if __name__ == "__main__":
    # Быстрый тест подключения при прямом запуске файла
    connect_and_get_postgres_info()