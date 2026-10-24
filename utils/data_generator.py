import random
import uuid

from faker import Faker

fake = Faker()

class DataGenerator:
    @staticmethod
    def generate_random_email():
        return fake.email()

    @staticmethod
    def generate_random_name():
        # Генерим имя длинее 5 символов, чтобы бэкенд не ругался
        return fake.name()

    @staticmethod
    def generate_random_password():
        # Всегда содержит заглавную, строчную букву, цифру и спецсимвол, длина 10 символов
        return "Test1234@"

        # ---- Movies ----

    @staticmethod
    def generate_movie_name() -> str:
        return f"Movie {uuid.uuid4().hex[:10]}"

    @staticmethod
    def generate_movie_payload(genre_id: int | None = None) -> dict:
        """
        Валидный payload для POST /movies согласно CreateMovieDto.
        genreId лучше брать из GET /genres — передайте его аргументом,
        если хотите гарантировать существующий жанр.
        """
        return {
            "name": DataGenerator.generate_movie_name(),
            "imageUrl": f"https://picsum.photos/200/300?r={uuid.uuid4().hex[:6]}",
            "price": random.randint(100, 1000),
            "description": fake.sentence(nb_words=10),
            "location": random.choice(["MSK", "SPB"]),
            "published": True,
            "genreId": genre_id if genre_id is not None else random.randint(1, 10),
        }