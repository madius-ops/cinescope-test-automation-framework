import pytest
from sqlalchemy.orm import Session
from db_requester.models import AccountTransactionTemplate
from utils.data_generator import DataGenerator
from db_requester.db_models.movie import MovieDBModel
from datetime import datetime, timezone

def test_accounts_transaction_template(db_session: Session):
    # ====================================================================== Подготовка к тесту
    # Создаем новые записи в базе данных (чтоб точно быть уверенными что в базе присутствуют данные для тестирования)

    stan = AccountTransactionTemplate(user=f"Stan_{DataGenerator.generate_random_int(10)}", balance=100)
    bob = AccountTransactionTemplate(user=f"Bob_{DataGenerator.generate_random_int(10)}", balance=500)

    # Добавляем записи в сессию
    db_session.add_all([stan, bob])
    # Фиксируем изменения в базе данных
    db_session.commit()

    def transfer_money(session, from_account, to_account, amount):
        # пример функции выполняющей транзакцию
        # представим что она написана на стороне тестируемого сервиса
        # и вызывая метод transfer_money, мы какбудтобы делем запрос в api_manager.movies_api.transfer_money
        """
        Переводит деньги с одного счета на другой.
        :param session: Сессия SQLAlchemy.
        :param from_account_id: ID счета, с которого списываются деньги.
        :param to_account_id: ID счета, на который зачисляются деньги.
        :param amount: Сумма перевода.
        """
        # Получаем счета
        from_account = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
        to_account = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()

        # Проверяем, что на счете достаточно средств
        if from_account.balance < amount:
            raise ValueError("Недостаточно средств на счете")

        # Выполняем перевод
        from_account.balance -= amount
        to_account.balance += amount

        # Сохраняем изменения
        session.commit()

    # ====================================================================== Тест
    # Проверяем начальные балансы
    assert stan.balance == 100
    assert bob.balance == 500

    try:

        with pytest.raises(ValueError, match="Недостаточно средств на счете"):
            transfer_money(db_session, from_account=stan.user, to_account=bob.user, amount=200)

        # Проверяем, что балансы изменились
        assert stan.balance == 100, "Баланс Стена изменился, хотя транзакция должна была упасть!"
        assert bob.balance == 500, "Баланс Боба изменился, хотя транзакция должна была упасть!"

    finally:
        # Удаляем данные для тестирования из базы
        db_session.delete(stan)
        db_session.delete(bob)
        # Фиксируем изменения в базе данных
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