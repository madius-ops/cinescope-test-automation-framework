from models.base_models import RegisterUserResponse


class TestUsersApi:  # Переименовали, чтобы не было конфликта с моделью TestUser

    def test_create_user(self, super_admin, creation_user_data):
        # Отправляем Pydantic-модель creation_user_data (реквестер сам ее переведет в JSON)
        response = super_admin.api.user_api.create_user(creation_user_data)

        # Валидируем ответ через Pydantic (сразу проверяются все типы и регулярки)
        valid_response = RegisterUserResponse(**response.json())

        # Обращаемся к данным через точку, так как теперь это объекты
        assert valid_response.id != "", "ID должен быть не пустым"
        assert valid_response.email == creation_user_data.email
        assert valid_response.fullName == creation_user_data.fullName
        assert valid_response.roles[0].value == creation_user_data.roles[0]
        assert valid_response.verified is True

    def test_get_user_by_locator(self, super_admin, creation_user_data):
        created_user_response = super_admin.api.user_api.create_user(creation_user_data).json()

        # Получаем юзеров по ID и Email
        response_by_id = super_admin.api.user_api.get_user(created_user_response['id']).json()
        response_by_email = super_admin.api.user_api.get_user(creation_user_data.email).json()  # ТУТ ТОЧКА

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"

        # Можем тоже прогнать через валидатор для надежности
        valid_user = RegisterUserResponse(**response_by_id)

        assert valid_user.id != "", "ID должен быть не пустым"
        assert valid_user.email == creation_user_data.email
        assert valid_user.fullName == creation_user_data.fullName
        assert valid_user.roles[0].value == creation_user_data.roles[0]
        assert valid_user.verified is True

    def test_get_user_by_id_common_user(self, common_user):
        # У common_user (объекта класса User) почту тоже достаем через точку
        common_user.api.user_api.get_user(common_user.email, expected_status=403)
