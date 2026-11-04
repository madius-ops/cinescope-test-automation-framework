import pytest
from utils.data_generator import DataGenerator


def test_movie_lifecycle_db(super_admin, db_helper, existing_genre_id):
    # 1. Генерируем валидные данные фильма с существующим жанром
    movie_payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
    movie_name = movie_payload["name"]

    # Проверка 1: до начала тестирования в базе отсутствует фильм
    assert not db_helper.movie_exists_by_name(movie_name), (
        f"Фильм '{movie_name}' уже есть в базе до старта теста!"
    )

    # 2. Создаем фильм через API от имени супер-админа
    create_response = super_admin.api.movies_api.create_movie(movie_payload)
    assert create_response.status_code in (200, 201), (
        f"Ошибка при создании фильма через API: {create_response.text}"
    )

    movie_id = create_response.json()["id"]

    try:
        # Проверка 2: после вызова запроса на создание в базе появился фильм
        movie_in_db = db_helper.get_movie_by_id(movie_id)
        assert movie_in_db is not None, f"Фильм с ID {movie_id} не найден в БД!"
        assert movie_in_db.name == movie_name
        assert movie_in_db.price == movie_payload["price"]

        # 3. Удаляем фильм через API
        delete_response = super_admin.api.movies_api.delete_movie(movie_id)
        assert delete_response.status_code in (200, 204), (
            f"Ошибка при удалении фильма через API: {delete_response.text}"
        )

        # Сбрасываем кэш ORM-сессии, чтобы она перечитала данные из базы, а не брала объект из памяти
        db_helper.db_session.expire_all()

        # Проверка 3: после удаления фильма через API в базе также удаляется данный объект
        assert not db_helper.movie_exists_by_id(movie_id), (
            f"Фильм с ID {movie_id} всё ещё остался в базе после удаления через API!"
        )

    except Exception:
        # Страховка: подчищаем созданный фильм, если промежуточные ассерты упали
        try:
            super_admin.api.movies_api.delete_movie(movie_id)
        except Exception:
            pass
        raise