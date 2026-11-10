import allure
import pytest
from models.base_page import CinescopRegisterPage
from models.page_object_models import CineScopeMoviePage, CinescopLoginPage
from utils.data_generator import DataGenerator


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Фильма")
@allure.story("Публикация пользовательского отзыва")
@pytest.mark.ui
class TestMovieReview:

    @allure.title("Успешное оставление отзыва под фильмом зарегистрированным пользователем")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_leave_review_authorized_user(self, browser_page):
        # 1. Генерим свежие уникальные данные
        email = DataGenerator.generate_random_email()
        name = DataGenerator.generate_random_name()
        password = DataGenerator.generate_random_password()

        # 2. Быстрая регистрация чисто через UI
        register_page = CinescopRegisterPage(browser_page)
        register_page.open()
        register_page.register(f"QA {name}", email, password, password)
        register_page.assert_was_redirect_to_login_page()

        login_page = CinescopLoginPage(browser_page)
        login_page.login(email, password)
        login_page.assert_was_redirect_to_home_page()

        # 3. Переход на страницу фильма (например, наш живой 80619)
        movie_page = CineScopeMoviePage(browser_page)
        movie_page.open_movie(80619)

        # 4. Пишем и отправляем отзыв
        review_text = f"Тестовый отзыв {name}"
        movie_page.leave_review(review_text)

        # 5. Проверка и скриншот в Allure
        movie_page.make_screenshot_and_attach_to_allure()
        movie_page.assert_review_is_published(review_text)
