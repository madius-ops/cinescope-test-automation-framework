import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker

from resources.db_creds import MoviesDbCreds
from db_requester.db_models.movie import MovieDBModel
from db_requester.db_models.user import UserDBModel

# Формируем URL для подключения через твои рабочие креды
connection_string = (
    f"postgresql+psycopg2://{MoviesDbCreds.USERNAME}:{MoviesDbCreds.PASSWORD}@"
    f"{MoviesDbCreds.HOST}:{MoviesDbCreds.PORT}/{MoviesDbCreds.DATABASE_NAME}"
)
engine = create_engine(connection_string)


def sdl_alchemy_SQL():
    query = """
    SELECT id, email, full_name
    FROM public.users
    LIMIT 3;
    """
    print("--- Запуск sdl_alchemy_SQL (ищем живых юзеров) ---")
    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = result.fetchall()

        if rows:
            for row in rows:
                print(f"ID: {row.id} | Email: {row.email} | Name: {row.full_name}")
        else:
            print("Таблица public.users пустая!")


def sdl_alchemy_ORM():
    print("\n--- Запуск sdl_alchemy_ORM ---")
    Base = declarative_base()

    class User(Base):
        __tablename__ = 'users'
        id = Column(String, primary_key=True)
        email = Column(String)
        full_name = Column(String)
        password = Column(String)
        created_at = Column(DateTime)
        updated_at = Column(DateTime)
        verified = Column(Boolean)
        banned = Column(Boolean)
        roles = Column(String)

    Session = sessionmaker(bind=engine)
    session = Session()

    user_id = "ae5f12bf-7aa0-40cc-a8b1-761f76acc253"

    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Full Name: {user.full_name}")
            print(f"Password: {user.password}")
            print(f"Created At: {user.created_at}")
            print(f"Updated At: {user.updated_at}")
            print(f"Verified: {user.verified}")
            print(f"Banned: {user.banned}")
            print(f"Roles: {user.roles}")
        else:
            print(f"[ORM] Пользователь с id {user_id} не найден.")
    finally:
        session.close()


def check_movies_table():
    query = """
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'movies';
    """
    with engine.connect() as connection:
        result = connection.execute(text(query))
        for row in result:
            print(f"Колонка: {row.column_name:<20} | Тип: {row.data_type}")


def check_movie_orm():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        movie = session.query(MovieDBModel).first()
        if movie:
            print("--- Фильм найден через ORM ---")
            print(f"ID: {movie.id}")
            print(f"Название: {movie.name}")
            print(f"Цена: {movie.price}")
            print(f"Рейтинг: {movie.rating}")
            print(f"Опубликован: {movie.published}")
            print(f"Словарь: {movie.to_dict()}")
        else:
            print("Таблица movies пустая.")
    finally:
        session.close()


def check_create_user_db():
    Session = sessionmaker(bind=engine)
    session = Session()

    # Генерируем реальные поля для создания записи
    user_data = {
        "id": str(uuid.uuid4()),
        "email": f"autotest_{uuid.uuid4().hex[:6]}@example.com",
        "full_name": "Test DB User",
        "password": "hashed_secret_password",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "verified": True,
        "banned": False,
        "roles": "{USER}",
    }

    try:
        user = UserDBModel(**user_data)
        session.add(user)
        session.commit()
        session.refresh(user)

        print("\n--- Пользователь успешно создан в БД ---")
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Словарь модели: {user.to_dict()}")
    except Exception as e:
        session.rollback()
        print(f"Ошибка при создании пользователя: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    check_movie_orm()
    check_create_user_db()
    # check_movies_table()
    # sdl_alchemy_SQL()
    # sdl_alchemy_ORM()