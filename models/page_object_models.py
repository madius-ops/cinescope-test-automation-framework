import allure
from playwright.sync_api import Page
from models.base_page import BasePage

class CinescopRegisterPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.url = "https://dev-cinescope.coconutqa.ru/register"

        # Локаторы элементов
        self.home_button = "a[href='/' and text()='Cinescope']"
        self.all_movies_button = "a[href='/movies' and text()='Все фильмы']"

        self.full_name_input = "input[name='fullName']"
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.repeat_password_input = "input[name='passwordRepeat']"

        self.register_button = "button[data-qa-id='register_submit_button']"
        self.sign_button = "a[href='/login' and text()='Войти']"

    # Шапка страницы
    def go_to_home_page(self):
        """Переход на главную страницу."""
        self.page.click(self.home_button)
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/")  # Ожидание загрузки главной страницы

    def go_to_all_movies(self):
        """Переход на страницу 'Все фильмы'."""
        self.page.click(self.all_movies_button)
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/movies")  # Ожидание загрузки страницы

    # Тело страницы
    def open(self):
        """Переход на страницу регистрации."""
        self.page.goto(self.url)

    def enter_full_name(self, full_name: str):
        """Ввод full_name"""
        self.page.fill(self.full_name_input, full_name)

    def enter_email(self, email: str):
        """Ввод email"""
        self.page.fill(self.email_input, email)

    def enter_password(self, password: str):
        """Ввод пароля"""
        self.page.fill(self.password_input, password)

    def enter_repeat_password(self, password: str):
        """Ввод подтверждения пароля"""
        self.page.fill(self.repeat_password_input, password)

    def click_register_button(self):
        """Клик по кнопке регистрации"""
        self.page.click(self.register_button)

    # Вспомогательные action методы
    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        """Полный процесс регистрации."""
        self.enter_full_name(full_name)
        self.enter_email(email)
        self.enter_password(password)
        self.enter_repeat_password(confirm_password)
        self.click_register_button()

    def wait_redirect_to_login_page(self):
        """Переход на страницу login."""
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/login")  # Ожидание загрузки страницы login
        assert self.page.url == "https://dev-cinescope.coconutqa.ru/login", "Редирект на домашнюю старницу не произошел"

    def check_allert(self):
        """Проверка всплывающего сообщения после редиректа"""
        # Проверка появления алерта с текстом "Подтвердите свою почту"
        notification_locator = self.page.get_by_text("Подтвердите свою почту")
        notification_locator.wait_for(state="visible")  # Ждем появления элемента

        assert notification_locator.is_visible(), "Уведомление не появилось"
        # Ожидание исчезновения алерта
        notification_locator.wait_for(state="hidden")  # Ждем, пока алерт исчезнет
        assert notification_locator.is_visible() == False, "Уведомление исчезло"


class CinescopLoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.url = "https://dev-cinescope.coconutqa.ru/login"

        # Локаторы элементов
        self.home_button = "a[href='/' and text()='Cinescope']"
        self.all_movies_button = "a[href='/movies' and text()='Все фильмы']"

        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"

        self.login_button = "button[data-qa-id='login_submit_button']"
        self.register_button = "a[href='/register' and text()='Зарегистрироваться']"

    # Обработчики локаторов на шапке страницы
    def go_to_home_page(self):
        """Переход на главную страницу"""
        self.page.click(self.home_button)
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/")  # Ожидание загрузки главной страницы

    def go_to_all_movies(self):
        """Переход на страницу 'Все фильмы'"""
        self.page.click(self.all_movies_button)
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/movies")  # Ожидание загрузки страницы

    # Обработчики локаторов на теле страницы
    def open(self):
        """Переход на страницу входа"""
        self.page.goto(self.url)

    def enter_email(self, email: str):
        """Ввод email"""
        self.page.fill(self.email_input, email)

    def enter_password(self, password: str):
        """Ввод пароля"""
        self.page.fill(self.password_input, password)

    def click_login_button(self):
        """Клик по кнопке входа"""
        self.page.click(self.login_button)

    # Вспомогательные action методы
    def login(self, email: str, password: str):
        """Полный процесс входа"""
        self.enter_email(email)
        self.enter_password(password)
        self.click_login_button()

    # ВОТ ЭТОТ МЕТОД НУЖНО ДОБАВИТЬ:
    def assert_was_redirect_to_home_page(self):
        self.wait_redirect_for_url(self.home_url)

    # И ВОТ ЭТОТ ДЛЯ АЛЕРТА:
    def assert_allert_was_pop_up(self):
        self.check_pop_up_element_with_text("Вы вошли в аккаунт")

    def wait_redirect_to_home_page(self):
        """Ожидание перехода на домашнюю страницу"""
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/")  # Ожидание загрузки домашней страницы
        assert self.page.url == "https://dev-cinescope.coconutqa.ru/", "Редирект на домашнюю старницу не произошел"

    def check_allert(self):
        """Проверка всплывающего сообщения после редиректа"""
        # Проверка появления алерта с текстом "Вы вошли в аккаунт"
        notification_locator = self.page.get_by_text("Вы вошли в аккаунт")
        notification_locator.wait_for(state="visible")  # Ждем появления элемента
        assert notification_locator.is_visible(), "Уведомление не появилось"

        # Ожидание исчезновения алерта
        notification_locator.wait_for(state="hidden")  # Ждем, пока алерт исчезнет
        assert notification_locator.is_visible() == False, "Уведомление исчезло"

class CineScopeMoviePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Локаторы страницы фильма и формы отзыва
        self.review_textarea = "textarea[name='review'], textarea[placeholder*='отзыв']"
        self.submit_review_button = "button[data-qa-id='movie_review_submit_button']"
        # Если оценка выставляется радиокнопками/звёздами (data-qa или селектор)
        self.rating_star = "button[data-qa-id='rate-movie-btn'], .rating-star"
        self.submit_review_button = "button[data-qa-id='submit-review-btn'], button:has-text('Отправить отзыв')"
        self.reviews_list = "div[data-qa-id='reviews-container'], .reviews-block"

    @allure.step("Открытие страницы фильма по id: {movie_id}")
    def open_movie(self, movie_id: int):
        self.open_url(f"{self.home_url}movies/{movie_id}")

    @allure.step("Оставление отзыва с текстом: '{review_text}'")
    def leave_review(self, review_text: str):
        # 1. Вводим текст
        self.enter_text_to_element(self.review_textarea, review_text)

        # 2. Находим кнопку по data-qa-id
        submit_btn = self.page.locator("button[data-qa-id='movie_review_submit_button']")

        # 3. Скроллим прямо к кнопке, чтобы она точно была на экране
        submit_btn.scroll_into_view_if_needed()

        # 4. Пробиваем клик с force=True (игнорирует перекрытия и проверки наведения)
        submit_btn.click(force=True)

    @allure.step("Проверка наличия отзыва на странице")
    def assert_review_is_published(self, review_text: str):
        with allure.step(f"Проверка отображения текста отзыва: '{review_text}'"):
            review_locator = self.page.locator(f"text={review_text}")
            review_locator.wait_for(state="visible", timeout=10000)
            assert review_locator.is_visible(), f"Отзыв '{review_text}' не отобразился на странице"