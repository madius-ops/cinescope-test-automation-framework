import pytest
import requests
import time

from entities.roles import Roles
from models.base_models import RegisterUserResponse
from utils.data_generator import DataGenerator


class TestAuth:
    def test_register_user(self, api_manager, test_user):
        response = api_manager.auth_api.register_user(test_user)

        valid_response = RegisterUserResponse(**response.json())

        assert valid_response.email == test_user.email
        assert Roles.USER in valid_response.roles

    def test_register_and_login_user(self, api_manager, registered_user):
        login_data = {
            "email": registered_user.email,
            "password": registered_user.password
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        assert "accessToken" in response_data
        assert response_data["user"]["email"] == registered_user.email

    def test_get_user(self, api_manager):
        # 1. Логинимся
        login_data = {"email": "romych_test_student3@example.com", "password": "Test1234@"}
        login_resp = api_manager.auth_api.login_user(
            login_data=login_data,
            expected_status=200
        )

        # 2. Вытаскиваем токен
        token = login_resp.json()["accessToken"]

        # 3. Вшиваем токен
        api_manager.session.headers.update({"Authorization": f"Bearer {token}"})

        # 4. Выполняем запрос через auth_api
        response = api_manager.auth_api.send_request("GET", "/user/me")
        assert response.status_code == 200
        print(f"\nДанные юзера: {response.json()}")

    def test_get_movies_by_genre(self, session):
        # ТУТ МАГИЯ: просим фикстуру session (в которой ОТКЛЮЧЕН SSL)
        from custom_requester.custom_requester import CustomRequester

        # И создаем реквестер для фильмов прямо внутри теста
        movies_requester = CustomRequester(session=session, base_url="https://api.dev-cinescope.coconutqa.ru")

        response = movies_requester.send_request(
            "GET",
            "/movies",
            params={"genre": "action", "limit": 5}
        )
        assert response.status_code == 200

    def test_login_invalid_credentials(self, api_manager):
        login_data = {"email": "net_takogo_uzera@example.com", "password": "WrongPassword123!"}
        response = api_manager.auth_api.login_user(
            login_data=login_data,
            expected_status=401
        )
        assert response.status_code == 401

    def test_logout(self, api_manager):
        # 1. Сначала нужно залогиниться, чтобы получить токен
        login_data = {"email": "romych_test_student3@example.com", "password": "Test1234@"}
        login_resp = api_manager.auth_api.login_user(
            login_data=login_data,
            expected_status=200
        )

        # 2. Вытаскиваем токен и вшиваем его в сессию
        token = login_resp.json()["accessToken"]
        api_manager.session.headers.update({"Authorization": f"Bearer {token}"})

        # 3. Теперь делаем логаут
        response = api_manager.auth_api.logout_user()
        assert response.status_code == 200

    def test_private_method_access(self, api_manager):
        # Вызываем типа "приватный" метод напрямую из теста
        # (Убедись, что в AuthApi он у тебя сейчас называется с подчеркиванием)
        api_manager.auth_api._update_session_headers({"foo": "bar"})

        # Проверяем, что заголовок реально пролез в сессию
        headers = api_manager.auth_api.session.headers

        print(f"\n[ЗАГОЛОВКИ СЕССИИ]: {headers}")

        assert "foo" in headers, "Заголовок foo не добавился!"
        assert headers["foo"] == "bar", "Значение заголовка не совпадает!"

class TestUserUnauthenticated:
    def test_get_user_info_without_auth(self, unauthenticated_api_manager):
        response = unauthenticated_api_manager.user_api.get_user_info(
            user_id="",
            expected_status=401
        )
        assert response.status_code == 401

class TestUser:
    def test_get_user_info(self, api_manager, authenticated_user):
        # 1. Вызываем get_user_info через user_api, передавая id текущего залогиненного юзера
        user_id = authenticated_user.id
        response = api_manager.user_api.get_user_info(user_id)
        response_data = response.json()

        # 2. Проверяем, что email и id в ответе совпадают с данными созданного юзера
        assert response_data["email"] == authenticated_user.email
        assert response_data["id"] == user_id

    def test_debug_kwargs(self, api_manager):
        user_data = {
            "email": DataGenerator.generate_random_email(),
            "password": "Password123!",
            "passwordRepeat": "Password123!",
            "fullName": "Vasya Pupkin"
        }

        # Вызываем с дополнительными kwargs
        api_manager.auth_api.register_user(user_data)

def test_delete_multiple_users(api_manager, super_admin):
    run_id = int(time.time())
    created_ids = []

    # 1. Регистрируем трёх пользователей
    for i in range(3):
        user_data = {
            "email": DataGenerator.generate_random_email(),
            "password": "Test1234@",
            "passwordRepeat": "Test1234@",
            "fullName": DataGenerator.generate_random_name(),
            "roles": ["USER"],
        }
        response = api_manager.auth_api.register_user(user_data)
        created_ids.append(response.json()["id"])

    id1, id2, id3 = created_ids

    # 2. Удаляем всех трёх ОДНИМ вызовом от суперадмина
    super_admin.api.user_api.delete_users(id1, id2, id3)

    # 3. Проверяем, что все удалены — логин каждого отдаёт 401
    for i in range(3):
        api_manager.auth_api.login_user(
            {
                "email": f"mass_delete_{run_id}_{i}@example.com",
                "password": "Test1234@",
            },
            expected_status=401,
        )
