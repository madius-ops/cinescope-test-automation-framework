# CineScope Test Automation Framework

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-9.x-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-UI-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-V2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Allure](https://img.shields.io/badge/Allure-Reporting-FFA000?style=for-the-badge&logo=allure&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

Комплексный модульный фреймворк для автоматизированного тестирования полнофункционального мультимедийного веб-сервиса **CineScope** (каталог фильмов, личные кабинеты, пользовательские отзывы, рейтинги и биллинговые сценарии).

Фреймворк сочетает сквозное тестирование **REST API**, валидацию целостности данных на уровне **PostgreSQL** и **E2E UI-сценарии** на **Playwright**.

---

## 🏗 Архитектурные особенности

- **Layered Architecture:** четкое разделение ответственности между клиентами API, бизнес-моделями, слоем доступа к БД и тестами.
- **Custom HTTP Client (`CustomRequester`):**
  - Обертка над `requests.Session` с настраиваемым пулом соединений и адаптером TLS (`TLSAdapter`).
  - Автоматическое логирование исходящих запросов и входящих ответов в формате **cURL** для ускоренной локализации дефектов.
  - Централизованное управление Bearer JWT-токенами и кастомными заголовками.
- **Контрактная валидация (Pydantic V2):**
  - Строгая типизация запросов и ответов (`BaseModel`).
  - Кастомные валидаторы `@field_validator` (проверка совпадения паролей, валидация формата ISO 8601 для дат, regex для почтовых адресов).
- **Сквозная верификация БД (SQLAlchemy + psycopg2):**
  - Прямое взаимодействие с базой данных PostgreSQL для проверки корректности записи (`INSERT` vs `UPDATE`).
  - Проверка жизненного цикла сущностей (API → DB → Delete → DB) с принудительной инвалидацией кэша ORM (`db_session.expire_all()`).
- **UI Automation (Playwright & Page Object Model):**
  - Использование паттерна **Page Object Model (POM)**: изолированные классы страниц (`LoginPage`, `RegisterPage`, `MoviePage`).
  - Автоожидание элементов (auto-waiting), работа с модальными окнами, проверка редиректов.
  - Автоматический захват скриншотов на ключевых шагах и при сбоях с аттачем в Allure.
- **Управление тестовыми данными:**
  - Генерация динамических уникальных данных через `Faker` (`DataGenerator`).
  - Иерархия фикстур `pytest` с авто-очисткой ресурсов (`yield`-тирдаун).
- **Отказоустойчивость и отчетность:**
  - Автоматический перезапуск нестабильных тестов с помощью `pytest-rerunfailures`.
  - Мягкие проверки (`soft assertions`) через `pytest-check`.
  - Детальные отчеты в **Allure Report** с группировкой по `@allure.epic`, `@allure.feature`, `@allure.story` и `@allure.severity`.

---

## 📁 Структура проекта

```text
cinescope-aqa-framework/
├── clients/                  # Микросервисные API-клиенты
│   ├── api_manager.py        # Фасадный менеджер клиентов (ApiManager)
│   ├── auth_api.py           # Клиент авторизации и регистрации
│   ├── movies_api.py         # Клиент управления фильмами
│   ├── genres_api.py         # Клиент каталога жанров
│   └── user_api.py           # Клиент профилей пользователей
├── custom_requester/         # Кастомная обертка над HTTP-сессией
│   └── custom_requester.py   # Логирование cURL, TLSAdapter, сессии
├── db_requester/             # Слой работы с базой данных
│   ├── db_client.py          # Сессии SQLAlchemy, engine, подключение
│   ├── db_helpers.py         # Хелперы для валидации таблиц и записей
│   └── models.py             # ORM-модели таблиц PostgreSQL
├── models/                   # Модели данных и Page Objects
│   ├── base_models.py        # Pydantic V2 схемы и контракты
│   ├── base_page.py          # Базовый класс страницы Playwright
│   └── page_object_models.py # Page Objects (LoginPage, MoviePage и др.)
├── tests/                    # Наборы автоматизированных тестов
│   ├── api/                  # Тесты REST API и интеграции с БД
│   │   ├── test_auth.py
│   │   ├── tests_movies.py
│   │   ├── test_movies_db.py # API + PostgreSQL E2E тесты
│   │   └── tests_users.py
│   └── ui/                   # E2E UI-тесты на Playwright
│       ├── test_login_page.py
│       ├── test_registration_page.py
│       └── test_movie_review.py
├── utils/                    # Вспомогательные утилиты
│   └── data_generator.py     # Фабрика тестовых данных (Faker)
├── conftest.py               # Корневые фикстуры, скоупы и тирдаун
├── pytest.ini                # Конфигурация запуска и логирования pytest
└── requirements.txt          # Зависимости проекта
```

---

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/madius-ops/cinescope-aqa-framework.git
cd cinescope-aqa-framework
```

### 2. Создание и активация виртуального окружения
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

### 4. Настройка переменных окружения
Создайте файл `.env` в корне проекта (по шаблону `.env.example`):
```env
BASE_URL=https://cinescope.example.com
DB_HOST=localhost
DB_PORT=5432
DB_NAME=movies_db
DB_USER=postgres
DB_PASSWORD=secret
```

---

## 🧪 Запуск тестов

### Запуск всех тестов:
```bash
pytest -v
```

### Запуск только API-тестов:
```bash
pytest -v tests/api/
```

### Запуск E2E тестов с базой данных (PostgreSQL):
```bash
pytest -v tests/api/test_movies_db.py
```

### Запуск UI-тестов (Playwright):
```bash
pytest -v tests/ui/
```

### Запуск с формированием отчета Allure:
```bash
pytest -v --alluredir=allure-results
allure serve allure-results
```

---

## 🐳 Запуск в Docker

Для запуска автотестов в изолированном окружении:

```bash
docker build -t cinescope-aqa .
docker run --rm -v $(pwd)/allure-results:/app/allure-results cinescope-aqa
```

---

## 📊 Отчетность (Allure Report)

Отчеты содержат:
- Иерархическую структуру: **Epic → Feature → Story → Test Case**
- Прикрепленные скриншоты интерфейса при прохождении ключевых шагов и сбоях
- Подробные cURL-логи каждого отправленного HTTP-запроса и полученного ответа
- Уровни критичности (Severity) и стек-трейсы ошибок

---

## 👤 Автор
- **GitHub:** [@madius-ops](https://github.com/madius-ops)
- **Роль:** QA Automation Engineer (Python)
