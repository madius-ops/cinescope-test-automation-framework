import time
import uuid

import requests
import pytest
from playwright.sync_api import sync_playwright
from clients.api_manager import ApiManager
from entities.roles import Roles
from entities.user import User
from models.base_models import TestUser, RegisterUserResponse
from resources.user_creds import SuperAdminCreds
from utils.data_generator import DataGenerator
from sqlalchemy.orm import Session
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper

@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(session)


@pytest.fixture
def test_user() -> TestUser:
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER.value]
    )


@pytest.fixture(scope="function")
def registered_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    test_user.id = response["id"]
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
    test_user.id = response_data.get("id")

    # 2. Логинимся под этим же юзером, чтобы получить accessToken
    login_data = {
        "email": test_user.email,
        "password": test_user.password
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
def created_movie(super_admin, existing_genre_id):
    payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
    response = super_admin.api.movies_api.create_movie(payload)
    movie_id = response.json()["id"]

    yield movie_id, payload
    try:
        super_admin.api.movies_api.delete_movie(movie_id, expected_status=200)
    except ValueError:
        pass

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

@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture(scope="function")
def creation_user_data(test_user):
    return test_user.model_copy(update={"verified": True, "banned": False})

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user

@pytest.fixture
def admin_data(test_user):
    # Добавляем случайный суффикс, чтобы email гарантированно не конфликтовал в БД
    unique_email = f"admin_{uuid.uuid4().hex[:6]}_{test_user.email}"
    return test_user.model_copy(update={
        "email": unique_email,
        "verified": True,
        "banned": False,
        "roles": [str(Roles.ADMIN.value)]
    })

@pytest.fixture
def admin(user_session, admin_data,super_admin):
    api = user_session()
    admin = User(
        admin_data.email,
        admin_data.password,
        [Roles.ADMIN.value],
        api=api,
    )
    super_admin.api.user_api.create_user(admin_data)
    admin.api.auth_api.authenticate(admin.creds)
    return admin


def test_register_user(api_manager: ApiManager, registration_user_data):
    response = api_manager.auth_api.register_user(user_data=registration_user_data)
    register_user_response = RegisterUserResponse(**response.json())
    assert register_user_response.email == registration_user_data.email, "Email не совпадает"

@pytest.fixture(scope="module")
def db_session() -> Session:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    yield db_session
    db_session.close()

@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    """
    Фикстура для экземпляра хелпера
    """
    db_helper = DBHelper(db_session)
    return db_helper

@pytest.fixture(scope="function")
def created_test_user(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user
    # Cleanup после теста
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)

@pytest.fixture
def delay_between_retries():
    time.sleep(2)  # Пауза в 2 секунды между попытками
    yield

@pytest.fixture(scope="function")
def browser_page():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        yield page

        context.close()
        browser.close()