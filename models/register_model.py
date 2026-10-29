from typing import Optional
from pydantic import BaseModel, Field, ValidationError, field_validator
from entities.roles import Roles
from venv import logger

class RegisteredUser(BaseModel):
    email: str
    fullName: str
    password: str = Field(..., min_length=8, description="Пароль от 8 символов")
    passwordRepeat: str = Field(..., min_length=8)
    roles: list[Roles]
    banned: Optional[bool] = None
    verified: Optional[bool] = None

    @field_validator("email")
    def check_email_at_symbol(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Ебать, мыло без '@'? Так не пойдет.")
        return value

def test_user_registration_data(registration_user_data):
    # Pydantic сам прогонит валидацию типов
    user = RegisteredUser(**registration_user_data)

    # Теперь к полям можно обращаться через точку, а IDE будет давать подсказки
    assert "@" in user.email
    assert user.password == user.passwordRepeat
    print(f"Создан юзер: {user.fullName}, Роль: {user.roles[0]}")


def test_pydantic_serialization(test_user, creation_user_data):
    # 1. Валидируем обе фикстуры (Pydantic сожрет их без ошибок)
    user_basic = RegisteredUser(**test_user)
    user_created = RegisteredUser(**creation_user_data)

    # 2. Переводим в JSON по условиям задачи
    # exclude_unset=True выкинет все поля, которые мы не передавали явно
    basic_json = user_basic.model_dump_json(exclude_unset=True)

    # Обычный дамп оставит всё как есть, включая None или явно переданные значения
    created_json = user_created.model_dump_json()

    # 3. Логируем
    logger.info(f"BASIC USER JSON: {basic_json}")
    logger.info(f"CREATED USER JSON: {created_json}")


def test_pydantic_custom_validators():
# --- УСПЕШНЫЙ КЕЙС ---
    valid_data = {
        "email": "roma@cinescope.com",
        "fullName": "Roman",
        "password": "Password123!",
        "passwordRepeat": "Password123!",
        "roles": ["USER"]
    }
    good_user = RegisteredUser(**valid_data)
    logger.info(f"✅ Успешная валидация! Юзер: {good_user.email}, Пароль: {good_user.password}")

    # --- ОШИБКА 1: НЕТ СОБАКИ В EMAIL ---
    bad_email_data = valid_data.copy()
    bad_email_data["email"] = "romacinescope.com"  # Убрали @

    try:
        RegisteredUser(**bad_email_data)
    except ValidationError as e:
        logger.error(f"❌ Ожидаемая ошибка (кривое мыло):\n{e}")

    # --- ОШИБКА 2: КОРОТКИЙ ПАРОЛЬ ---
    bad_password_data = valid_data.copy()
    bad_password_data["password"] = "12345"  # Слишком короткий

    try:
        RegisteredUser(**bad_password_data)
    except ValidationError as e:
        logger.error(f"❌ Ожидаемая ошибка (короткий пароль):\n{e}")