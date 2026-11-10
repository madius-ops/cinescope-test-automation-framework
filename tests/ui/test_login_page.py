import time
import allure
import pytest
from playwright.sync_api import sync_playwright
from models.page_object_models import CinescopLoginPage

def test_login_by_ui(registered_user):
   with sync_playwright() as playwright:
        # Запуск браузера
        browser = playwright.chromium.launch(headless=False)  # headless=False для визуального отображения
        page = browser.new_page()

        # Создаем объект страницы регистрации cinescope
        login_page = CinescopLoginPage(page)

        # Открываем страницу
        login_page.open()
        login_page.login(registered_user.email, registered_user.password)

        # Проверка редиректа на домашнюю страницу
        login_page.wait_redirect_to_home_page()

        # Проверка появления и исчезновения алерта
        login_page.check_allert()

        # Пауза для визуальной проверки (нужно удалить в реальном тестировании)
        time.sleep(5)

        # Закрываем браузер
        browser.close()

@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Login")
@pytest.mark.ui
class TestLoginPage:
    @allure.title("Проведение успешного входа в систему")
    def test_login_by_ui(self, registered_user):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()
            login_page = CinescopLoginPage(page)

            login_page.open()
            login_page.login(registered_user.email, registered_user.password)

            # Проверки редиректа, скриншот и алерт
            login_page.assert_was_redirect_to_home_page()
            login_page.make_screenshot_and_attach_to_allure()
            login_page.assert_allert_was_pop_up()

            browser.close()