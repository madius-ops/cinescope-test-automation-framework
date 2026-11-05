import allure
import pytest
from pytest_check import check
from sqlalchemy.orm import Session

from db_requester.db_models.movie import MovieDBModel, MovieItemResponse, MoviesListResponse
from utils.data_generator import DataGenerator


@allure.epic("CineScope Service")
@allure.feature("Movies API")
@pytest.mark.api
class TestMoviesPositive:

    @allure.story("Создание фильма")
    @allure.title("Успешное создание фильма супер-администратором")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_create_movie(self, super_admin, existing_genre_id):
        with allure.step("Генерация тестовых данных фильма"):
            payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)

        with allure.step("Отправка POST-запроса на создание фильма"):
            response = super_admin.api.movies_api.create_movie(payload)
            body = response.json()

        with allure.step("Проверка статус-кода и полей ответа"):
            assert response.status_code == 201
            assert body["name"] == payload["name"]
            assert body["price"] == payload["price"]
            assert body["location"] == payload["location"]
            assert body["genreId"] == payload["genreId"]
            assert "id" in body

        with allure.step("Очистка созданных данных (удаление фильма)"):
            super_admin.api.movies_api.delete_movie(body["id"], expected_status=200)

    @allure.story("Получение списка фильмов")
    @allure.title("Получение общего списка фильмов с валидацией схемы Pydantic")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_movies_list(self, api_manager):
        with allure.step("Отправка GET-запроса на /movies"):
            response = api_manager.movies_api.get_movies()
            body = response.json()

        with allure.step("Базовая проверка структуры ответа"):
            assert response.status_code == 200
            assert isinstance(body, dict)
            assert "movies" in body
            assert isinstance(body["movies"], list)
            assert "count" in body
            assert "page" in body
            assert "pageSize" in body

        with allure.step("Валидация схемы списка через Pydantic (Пункт 5)"):
            MoviesListResponse.model_validate(body)

    @allure.story("Фильтрация фильмов")
    @allure.title("Фильтрация фильмов по жанру")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_movies_filter_by_genre(self, api_manager, created_movie):
        _, payload = created_movie
        target_genre = payload["genreId"]

        with allure.step(f"Запрос фильмов с genreId={target_genre}"):
            response = api_manager.movies_api.get_movies(
                params={"genreId": target_genre, "pageSize": 20}
            )
            body = response.json()["movies"]

        with allure.step("Проверка соответствия жанра у всех возвращенных фильмов"):
            assert response.status_code == 200
            assert all(m["genreId"] == target_genre for m in body)

    @allure.story("Фильтрация фильмов")
    @allure.title("Фильтрация фильмов по диапазону цен")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_movies_filter_by_price_range(self, api_manager, created_movie):
        _, payload = created_movie
        price = payload["price"]
        min_p = max(1, price - 50)
        max_p = price + 50

        with allure.step(f"Запрос фильмов с ценой от {min_p} до {max_p}"):
            response = api_manager.movies_api.get_movies(
                params={"minPrice": min_p, "maxPrice": max_p, "pageSize": 20}
            )
            body = response.json()["movies"]

        with allure.step("Проверка попадания цен в заданный диапазон"):
            assert response.status_code == 200
            assert all(min_p <= m["price"] <= max_p for m in body)

    @allure.story("Просмотр фильма")
    @allure.title("Получение фильма по ID и валидация единичной схемы")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_movie_by_id(self, api_manager, created_movie):
        movie_id, payload = created_movie

        with allure.step(f"Запрос фильма по id={movie_id}"):
            body = api_manager.movies_api.get_movie_by_id(movie_id).json()

        with allure.step("Валидация полей ответа"):
            assert body["id"] == movie_id
            assert body["name"] == payload["name"]
            assert "reviews" in body

        with allure.step("Валидация схемы отдельного фильма через Pydantic"):
            MovieItemResponse.model_validate(body)

    @allure.story("Редактирование фильма")
    @allure.title("Обновление названия фильма супер-администратором")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_update_movie(self, super_admin, created_movie):
        movie_id, _ = created_movie
        new_name = DataGenerator.generate_movie_name()

        with allure.step(f"Отправка запроса на обновление названия фильма на '{new_name}'"):
            super_admin.api.movies_api.update_movie(movie_id, {"name": new_name})

        with allure.step("Проверка обновленного названия через GET-запрос"):
            body = super_admin.api.movies_api.get_movie_by_id(movie_id).json()
            assert body["name"] == new_name

    @allure.story("Удаление фильма")
    @allure.title("Удаление фильма супер-администратором")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_delete_movie(self, super_admin, existing_genre_id):
        with allure.step("Создание тестового фильма"):
            payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
            movie_id = super_admin.api.movies_api.create_movie(payload).json()["id"]

        with allure.step(f"Удаление фильма id={movie_id}"):
            response = super_admin.api.movies_api.delete_movie(movie_id)
            assert response.status_code == 200

        with allure.step("Проверка, что фильм больше не существует (код 404)"):
            check_resp = super_admin.api.movies_api.get_movie_by_id(movie_id, expected_status=404)
            assert check_resp.status_code == 404

    @allure.story("Интеграция с базой данных")
    @allure.title("Проверка создания фильма в API с валидацией записи в БД (Пункт 4)")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_create_movie_matches_database(self, super_admin, existing_genre_id, db_session: Session):
        with allure.step("Генерация данных и создание фильма через API"):
            payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
            response = super_admin.api.movies_api.create_movie(payload)
            assert response.status_code == 201
            movie_api = response.json()
            movie_id = movie_api["id"]

        try:
            with allure.step("Запрос созданного фильма напрямую из PostgreSQL"):
                movie_db = db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).first()
                assert movie_db is not None, f"Фильм с id={movie_id} не найден в БД"

            with allure.step("Сверка полей между ответом API и БД через Soft Asserts"):
                with check:
                    check.equal(movie_api["name"], movie_db.name, "Не совпадает название фильма")
                    check.equal(movie_api["price"], movie_db.price, "Не совпадает цена")
                    check.equal(movie_api["location"], movie_db.location, "Не совпадает локация")
                    check.equal(movie_api["genreId"], movie_db.genre_id, "Не совпадает genreId")
        finally:
            with allure.step("Очистка данных (удаление созданного фильма)"):
                super_admin.api.movies_api.delete_movie(movie_id, expected_status=200)


@allure.epic("CineScope Service")
@allure.feature("Movies API")
@pytest.mark.api
@pytest.mark.negative
class TestMoviesNegative:

    @allure.story("Создание фильма (негативные сценарии)")
    @allure.title("Создание фильма без обязательного поля name")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_movie_without_name(self, super_admin, existing_genre_id):
        with allure.step("Формирование payload без поля name"):
            payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
            payload.pop("name", None)

        with allure.step("Отправка запроса и ожидание ошибки 400"):
            response = super_admin.api.movies_api.create_movie(payload, expected_status=400)
            assert response.status_code == 400

    @allure.story("Создание фильма (негативные сценарии)")
    @allure.title("Создание фильма с некорректным типом genreId")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_movie_with_invalid_genre_id(self, super_admin):
        with allure.step("Формирование payload с невалидным genreId"):
            payload = DataGenerator.generate_movie_payload()
            payload["genreId"] = "not-a-number"

        with allure.step("Отправка запроса и ожидание ошибки 400"):
            response = super_admin.api.movies_api.create_movie(payload, expected_status=400)
            assert response.status_code == 400

    @allure.story("Создание фильма (негативные сценарии)")
    @allure.title("Создание фильма с неизвестной локацией")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_movie_with_invalid_location(self, super_admin, existing_genre_id):
        with allure.step("Формирование payload с локацией UNKNOWN"):
            payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
            payload["location"] = "UNKNOWN"

        with allure.step("Отправка запроса и ожидание ошибки 400"):
            response = super_admin.api.movies_api.create_movie(payload, expected_status=400)
            assert response.status_code == 400

    @allure.story("Авторизация при работе с фильмами")
    @allure.title("Попытка создания фильма без авторизации (401)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_movie_without_auth(self, api_manager, existing_genre_id):
        with allure.step("Отправка запроса на создание неавторизованным клиентом"):
            payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
            response = api_manager.movies_api.create_movie(payload, expected_status=401)
            assert response.status_code == 401

    @allure.story("Авторизация при работе с фильмами")
    @allure.title("Попытка обновления фильма без авторизации (401)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_without_auth(self, api_manager, created_movie):
        movie_id, _ = created_movie
        with allure.step(f"Отправка запроса на обновление id={movie_id} без авторизации"):
            response = api_manager.movies_api.update_movie(
                movie_id, {"name": "Hacked"}, expected_status=401
            )
            assert response.status_code == 401

    @allure.story("Авторизация при работе с фильмами")
    @allure.title("Попытка удаления фильма без авторизации (401)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_without_auth(self, api_manager, created_movie):
        movie_id, _ = created_movie
        with allure.step(f"Отправка запроса на удаление id={movie_id} без авторизации"):
            response = api_manager.movies_api.delete_movie(movie_id, expected_status=401)
            assert response.status_code == 401

    @allure.story("Просмотр фильма")
    @allure.title("Запрос несуществующего фильма (404)")
    @allure.severity(allure.severity_level.MINOR)
    def test_get_movie_by_nonexistent_id(self, api_manager):
        with allure.step("Запрос фильма с несуществующим ID 999999999"):
            response = api_manager.movies_api.get_movie_by_id(999_999_999, expected_status=404)
            assert response.status_code == 404

    @allure.story("Редактирование фильма")
    @allure.title("Попытка обновления несуществующего фильма (404)")
    @allure.severity(allure.severity_level.MINOR)
    def test_update_nonexistent_movie(self, super_admin):
        with allure.step("Обновление фильма с несуществующим ID"):
            response = super_admin.api.movies_api.update_movie(
                999_999_999, {"name": "Ghost"}, expected_status=404
            )
            assert response.status_code == 404

    @allure.story("Удаление фильма")
    @allure.title("Попытка удаления несуществующего фильма (404)")
    @allure.severity(allure.severity_level.MINOR)
    def test_delete_nonexistent_movie(self, super_admin):
        with allure.step("Удаление фильма с несуществующим ID"):
            response = super_admin.api.movies_api.delete_movie(999_999_999, expected_status=404)
            assert response.status_code == 404

    @allure.story("Пагинация фильмов")
    @allure.title("Запрос с невалидным параметром page=0")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_movies_invalid_page(self, api_manager):
        with allure.step("Запрос фильмов с page=0"):
            response = api_manager.movies_api.get_movies(
                params={"page": 0}, expected_status=400
            )
            assert response.status_code == 400

    @allure.story("Пагинация фильмов")
    @allure.title("Запрос с выходом за лимит pageSize=21")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_movies_page_size_over_limit(self, api_manager):
        with allure.step("Запрос фильмов с pageSize=21"):
            response = api_manager.movies_api.get_movies(
                params={"pageSize": 21}, expected_status=400
            )
            assert response.status_code == 400

    @allure.story("Ролевая модель")
    @allure.title("Отказ в доступе на создание фильма обычному пользователю (403)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_movie_with_user_role(self, common_user, existing_genre_id):
        with allure.step("Попытка создания фильма клиентом с ролью USER"):
            payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
            response = common_user.api.movies_api.create_movie(payload, expected_status=403)
            assert response.status_code == 403


@allure.epic("CineScope Service")
@allure.feature("Movies API")
@pytest.mark.api
@pytest.mark.regression
class TestMoviesFiltering:

    @allure.story("Параметризованная фильтрация")
    @allure.title("Фильтрация фильмов по диапазону цен: [{min_p}, {max_p}]")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("min_p, max_p", [
        (100, 500),
        (1, 1000),
    ], ids=["range_100_500", "range_1_1000"])
    def test_filter_by_price_range(self, api_manager, min_p, max_p):
        with allure.step(f"Запрос фильмов с ценами в диапазоне [{min_p}, {max_p}]"):
            params = {"minPrice": min_p, "maxPrice": max_p}
            response = api_manager.movies_api.get_movies(params=params)
            data = response.json()
            movies = data["movies"]

        with allure.step("Проверка диапазона цен и валидация схемы"):
            assert len(movies) > 0, "Список фильмов пуст, нечего проверять"
            MoviesListResponse.model_validate(data)

            for movie in movies:
                assert min_p <= movie["price"] <= max_p, f"Цена {movie['price']} вылезла за пределы [{min_p}, {max_p}]"

    @allure.story("Параметризованная фильтрация")
    @allure.title("Фильтрация фильмов по локации: {location}")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("location", ["MSK", "SPB"], ids=["location_msk", "location_spb"])
    def test_filter_by_location(self, api_manager, location):
        with allure.step(f"Запрос фильмов для локации {location}"):
            params = {"locations": location}
            response = api_manager.movies_api.get_movies(params=params)
            data = response.json()
            movies = data["movies"]

        with allure.step("Проверка соответствия локации и схемы ответа"):
            assert len(movies) > 0, f"Список фильмов пуст для локации {location}"
            MoviesListResponse.model_validate(data)

            for movie in movies:
                assert movie['location'] == location, f"Локация {movie['location']} не совпадает с ожидаемой {location}"


@allure.epic("CineScope Service")
@allure.feature("Movies API")
@pytest.mark.api
@pytest.mark.regression
class TestMoviesDeletion:

    @allure.story("Ролевая модель удаления")
    @allure.title("Проверка прав на удаление фильма под ролью {user_fixture} (ожидаем {expected_status})")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("user_fixture, expected_status", [
        ("super_admin", 200),
        ("admin", 403),
        ("common_user", 403),
        ("unauthenticated_api_manager", 401)
    ], ids=["role_super_admin", "role_admin", "role_user", "unauthenticated"])
    def test_delete_movie_roles(self, request, created_movie, user_fixture, expected_status):
        with allure.step(f"Получение клиента для роли: {user_fixture}"):
            client = request.getfixturevalue(user_fixture)
            movie_id, _ = created_movie
            api = client.api.movies_api if hasattr(client, "api") else client.movies_api

        with allure.step(f"Отправка запроса на удаление фильма id={movie_id}"):
            api.delete_movie(movie_id, expected_status=expected_status)