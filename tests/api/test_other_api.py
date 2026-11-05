import random
import pytest
import allure
from sqlalchemy.orm import Session
from db_requester.models import AccountTransactionTemplate
from utils.data_generator import DataGenerator
from db_requester.db_models.movie import MovieDBModel
from datetime import datetime, timezone


@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
class TestAccountTransactionTemplate:

    @allure.story("Корректность перевода денег между двумя счетами")
    @allure.description("""
    Этот тест проверяет корректность перевода денег между двумя счетами.
    Шаги:
    1. Создание двух счетов: Stan и Bob.
    2. Перевод 200 единиц от Stan к Bob.
    3. Проверка изменения балансов.
    4. Очистка тестовых данных.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Ivan Petrovich")
    @allure.title("Тест перевода денег между счетами 200 рублей")
    def test_accounts_transaction_template(self, db_session: Session):
        # ====================================================================== Подготовка к тесту
        with allure.step("Создание тестовых данных в базе данных: счета Stan и Bob"):
            stan = AccountTransactionTemplate(user=f"Stan_{DataGenerator.generate_random_int(10)}", balance=1000)
            bob = AccountTransactionTemplate(user=f"Bob_{DataGenerator.generate_random_int(10)}", balance=500)
            db_session.add_all([stan, bob])
            db_session.commit()

        @allure.step("Функция перевода денег: transfer_money")
        @allure.description("""
            функция выполняющая транзакцию, имитация вызова функции на стороне тестируемого сервиса
            и вызывая метод transfer_money, мы какбудтобы делем запрос в api_manager.movies_api.transfer_money
            """)
        def transfer_money(session, from_account, to_account, amount):
            with allure.step(" Получаем счета"):
                from_account = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
                to_account = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()

            with allure.step("Проверяем, что на счете достаточно средств"):
                if from_account.balance < amount:
                    raise ValueError("Недостаточно средств на счете")

            with allure.step("Выполняем перевод"):
                from_account.balance -= amount
                to_account.balance += amount

            with allure.step("Сохраняем изменения"):
                session.commit()

        # ====================================================================== Тест
        with allure.step("Проверяем начальные балансы"):
            assert stan.balance == 1000
            assert bob.balance == 500

        try:
            with allure.step("Выполняем перевод 200 единиц от stan к bob"):
                transfer_money(db_session, from_account=stan.user, to_account=bob.user, amount=200)

            with allure.step("Проверяем, что балансы изменились"):
                assert stan.balance == 800
                assert bob.balance == 700

        except Exception as e:
            with allure.step("ОШИБКА откаты транзакции"):
                db_session.rollback()

            pytest.fail(f"Ошибка при переводе денег: {e}")

        finally:
            with allure.step("Удаляем данные для тестирования из базы"):
                db_session.delete(stan)
                db_session.delete(bob)
                db_session.commit()

class TestMovieAPI:
    def test_delete_movie(self, movies_api, db_session: Session, existing_genre_id):
        """
        Тест для удаления фильма с гарантированным наличием данных в БД перед стартом.
        """
        movie_id = 54

        # 1. Проверяем перед тестом, что в базе действительно есть фильм с данным ID
        movie_in_db = db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).first()

        # Если фильма нет — добавляем объект напрямую в базу со всеми обязательными полями
        if not movie_in_db:
            new_movie = MovieDBModel(
                id=movie_id,
                name="Фильм для теста удаления 54",
                price=300,
                description="Тестовый фильм, созданный напрямую в БД для проверки удаления",
                image_url="https://example.com/poster.jpg",
                rating=7.5,
                location="SPB",
                published=True,
                genre_id=existing_genre_id,
                created_at=datetime.now(timezone.utc)
            )
            db_session.add(new_movie)
            db_session.commit()

        # 2. Удаляем фильм через API (клиент уже авторизован)
        delete_response = movies_api.delete_movie(movie_id)
        assert delete_response.status_code == 200, "Фильм должен успешно удалиться"

        # 3. Проверяем через API, что фильм действительно удалён
        get_response = movies_api.get_movie_by_id(movie_id, expected_status=404)
        assert get_response.status_code == 404, "Фильм не должен существовать после удаления"

        # 4. Проверяем в самой базе данных, что запись стерта физически
        db_session.expire_all()
        assert db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).first() is None, (
            f"Фильм с ID {movie_id} все еще присутствует в базе данных после удаления через API!"
        )

    @allure.title("Тест с перезапусками")
    @pytest.mark.flaky(reruns=3)
    def test_with_retries(self, delay_between_retries):
        with allure.step("Шаг 1: Проверка случайного значения"):
            result = random.choice([True, False])
            assert result, "Тест упал, потому что результат False"