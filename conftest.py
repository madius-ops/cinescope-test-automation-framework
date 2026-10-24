import requests
import pytest
from clients.api_manager import ApiManager
from utils.data_generator import DataGenerator


@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(session)


@pytest.fixture(scope="function")
def test_user():
    password = DataGenerator.generate_random_password()
    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": password,
        "passwordRepeat": password,
        "roles": ["USER"]
    }


@pytest.fixture(scope="function")
def registered_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    test_user["id"] = response["id"]
    return test_user


@pytest.fixture(scope="session")
def unauthenticated_api_manager():
    # Создаем чистую сессию с отключенным SSL (если сервак опять начнет бузить)
    session = requests.Session()
    session.verify = False

    # Отдаем менеджер в тест
    yield ApiManager(session)

    # Закрываем сессию после того, как все тесты прошли
    session.close()


@pytest.fixture(scope="function")
def authenticated_user(api_manager, test_user):
    # 1. Регистрируем пользователя
    response = api_manager.auth_api.register_user(test_user)
    response_data = response.json()

    # Достаем ID из ответа регистрации (или логина)
    user_id = response_data.get("id")
    test_user["id"] = user_id

    # 2. Логинимся под этим же юзером, чтобы получить accessToken
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    login_response = api_manager.auth_api.login_user(login_data)
    token = login_response.json().get("accessToken")

    # 3. Вшиваем токен в заголовки сессии менеджера, чтобы запросы шли авторизованными
    api_manager.auth_api._update_session_headers({"Authorization": f"Bearer {token}"})

    # Возвращаем словарь с данными пользователя (включая id)
    return test_user

ADMIN_EMAIL = "api1@gmail.com"
ADMIN_PASSWORD = "asdqwe123Q"

@pytest.fixture(scope="session")
def admin_token(unauthenticated_api_manager):
    login_response = unauthenticated_api_manager.auth_api.login_user({
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
    })
    return login_response.json()["accessToken"]

@pytest.fixture(scope="function")
def created_movie(movies_api, existing_genre_id):
    """
    Создаёт фильм перед тестом (под админом) и удаляет после.
    Возвращает (movie_id, payload).
    """
    payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)

    response = movies_api.create_movie(payload)
    movie_id = response.json()["id"]

    yield movie_id, payload

    movies_api.delete_movie(movie_id, expected_status=200)

@pytest.fixture(scope="function")
def movies_api(admin_token):
    import requests
    session = requests.Session()
    session.verify = False
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {admin_token}",
    })
    api = ApiManager(session)
    yield api.movies_api
    session.close()

@pytest.fixture(scope="function")
def existing_genre_id(api_manager):
    """Реальный id жанра из GET /genres — чтобы genreId в payload был валидным."""
    genres = api_manager.genres_api.get_genres().json()
    assert genres, "GET /genres вернул пустой список"
    return genres[0]["id"]

