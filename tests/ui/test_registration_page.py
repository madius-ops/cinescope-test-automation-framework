import allure
import pytest
from models.base_page import CinescopRegisterPage
from utils.data_generator import DataGenerator


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Регистрации")
@pytest.mark.ui
class TestRegistrationPage:

    @allure.title("Успешная регистрация нового пользователя через интерфейс")
    def test_register_by_ui(self, browser_page):
        random_email = DataGenerator.generate_random_email()
        random_name = DataGenerator.generate_random_name()
        random_password = DataGenerator.generate_random_password()

        # Создаем объект страницы регистрации cinescope
        register_page = CinescopRegisterPage(browser_page)

        # Открываем страницу и регистрируемся
        register_page.open()
        register_page.register(f"PlaywrightTest {random_name}", random_email, random_password, random_password)

        # Проверка редиректа на страницу /login, скриншот и алерт
        register_page.assert_was_redirect_to_login_page()
        register_page.make_screenshot_and_attach_to_allure()
        register_page.assert_allert_was_pop_up()
