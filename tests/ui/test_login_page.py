import allure
import pytest
from models.page_object_models import CinescopLoginPage


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Login")
@pytest.mark.ui
class TestLoginPage:

    @allure.title("Проведение успешного входа в систему")
    def test_login_by_ui(self, browser_page, registered_user):
        login_page = CinescopLoginPage(browser_page)

        login_page.open()
        login_page.login(registered_user.email, registered_user.password)

        # Проверки редиректа, скриншот и алерт
        login_page.assert_was_redirect_to_home_page()
        login_page.make_screenshot_and_attach_to_allure()
        login_page.assert_allert_was_pop_up()
