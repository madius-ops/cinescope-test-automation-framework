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

Фреймворк реализует современный подход к **Fullstack QA**: сквозное тестирование **REST API**, строгая валидация схем и форматов через **Pydantic V2**, проверка целостности данных на уровне **PostgreSQL (SQLAlchemy)** и надежные **E2E UI-сценарии** на **Playwright**.

---

## 🎯 Стратегия автоматизации и подходы к тестированию (AQA Strategy)

В основу фреймворка заложена классическая **пирамида тестирования** с упором на скорость, стабильность и независимость тестов:
- **80% API & DB Integration Tests:** быстрое выполнение, контрактная валидация, проверка бизнес-логики и персистентности данных в базе.
- **20% E2E UI Tests:** проверка критических пользовательских путей (авторизация, регистрация, публикация отзывов) через реальный браузер.

### 📐 Применяемые техники тест-дизайна:
- **Классы эквивалентности (Equivalence Partitioning):** деление входных данных на валидные и невалидные группы для исключения избыточных проверок.
- **Анализ граничных значений (Boundary Value Analysis):** верификация граничных условий в полях ввода (длина пароля, форматы дат, диапазоны цен).
- **Попарное тестирование (Pairwise):** комбинаторное тестирование сложных фильтров каталога и матриц пользовательских ролей.
- **Параметризация `@pytest.mark.parametrize`:** лаконичные сценарии с наборами `(input_data, expected_status)` вместо дублирования кода.

### 📈 Метрики эффективности автоматизации:
| Метрика | Значение | Описание |
| :--- | :--- | :--- |
| **Регрессионный прогон** | **20 минут** (ранее 4.5 часа ручной проверки) | Ускорение обратной связи для команды разработки в 13 раз |
| **Покрытие критических эндпоинтов** | **>85%** | Полное покрытие модулей Auth, Movies, Users, Genres |
| **Стабильность (Flaky Rate)** | **<1%** | Достигнуто за счет 100% изоляции тестовых данных и автоожиданий Playwright |

---

## 🏗 Архитектурные особенности фреймворка

- **Layered Architecture:** четкое разделение ответственности между клиентами API, бизнес-моделями, слоем доступа к БД и тестами.
- **Custom HTTP Client (`CustomRequester`):**
  - Обертка над `requests.Session` с пулом соединений и адаптером `TLSAdapter` (обход строгих проверок SSL).
  - Автоматическое логирование исходящих запросов и входящих ответов в формате **cURL** для ускоренной локализации дефектов разработчиками.
  - Централизованное управление Bearer JWT-токенами и кастомными заголовками сессии.
- **Контрактная валидация (Pydantic V2):**
  - Строгая типизация запросов и ответов (`BaseModel`).
  - Кастомные валидаторы `@field_validator` (проверка совпадения паролей, валидация формата ISO 8601 для дат, regex для email).
  - Мгновенное падение тестов при нарушении контракта бэкендом с читаемыми логами ошибок в Allure.
- **Управление жизненным циклом сессий и краевыми случаями API:**
  - Гибкая параметризация `expected_status` в `CustomRequester` (например, обработка нестандартного `201 Created` при успешной генерации JWT-сессии на эндпоинте `/login`).
  - Строгий контроль порядка очистки ресурсов (Teardown): в сценариях массовой очистки (`delete_users`) пользователь-владелец Bearer-токена удаляется строго последним в очереди, что предотвращает преждевременную инвалидацию токена бэкендом и каскадные ошибки `401 Unauthorized`.
  - Безопасная распаковка `*args` и `**kwargs` для динамического проброса таймаутов, query-параметров и заголовков запросов.
- **Сквозная верификация БД (SQLAlchemy ORM + PostgreSQL):**
  - Прямое взаимодействие с базой данных PostgreSQL для проверки корректности записи (`INSERT` vs `UPDATE`).
  - Проверка жизненного цикла сущностей (API → DB → Delete → DB) с принудительной инвалидацией кэша ORM (`db_session.expire_all()`).
- **UI Automation (Playwright & Page Object Model):**
  - Использование паттерна **Page Object Model (POM)**: изолированные классы страниц (`LoginPage`, `RegisterPage`, `MoviePage`).
  - Встроенные автоожидания элементов (`auto-waiting`), исключающие костыли с `time.sleep`.
  - Автоматический захват скриншотов на ключевых шагах и при сбоях с аттачем в Allure.
- **Изоляция и управление тестовыми данными:**
  - Генерация динамических уникальных данных через `Faker` и `UUID` (`DataGenerator`) для предотвращения конфликтов `409 Conflict`.
  - Иерархия фикстур `pytest` с авто-очисткой ресурсов (`yield`-тирдаун).
- **Отказоустойчивость и отчетность:**
  - Автоматический перезапуск нестабильных тестов с помощью `pytest-rerunfailures`.
  - Мягкие проверки (`soft assertions`) через `pytest-check`.
  - Детальные отчеты в **Allure Report** с группировкой по `@allure.epic`, `@allure.feature`, `@allure.story` и `@allure.severity`.

---

## 📁 Структура проекта

```text
cinescope-test-automation-framework/
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
│   └── data_generator.py     # Фабрика тестовых данных (Faker + UUID)
├── conftest.py               # Корневые фикстуры, скоупы и тирдаун
├── pytest.ini                # Конфигурация запуска, маркеры и логирование
└── requirements.txt          # Зависимости проекта
```

---

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/madius-ops/cinescope-test-automation-framework.git
cd cinescope-test-automation-framework
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
BASE_URL=https://dev-cinescope.coconutqa.ru
DB_HOST=localhost
DB_PORT=5432
DB_NAME=movies_db
DB_USER=postgres
DB_PASSWORD=secret
```

---

## 🧪 Запуск тестов

### 🏷️ Запуск по тест-маркерам (Test Tagging):
```bash
# Запуск Smoke-тестов
pytest -v -m smoke

# Запуск Regression-сьюта
pytest -v -m regression

# Запуск только API-тестов
pytest -v -m api

# Запуск только UI-тестов
pytest -v -m ui
```

### 🚀 Параллельный запуск тестов (pytest-xdist):
```bash
pytest -v -n auto
```

### 🗄️ Запуск E2E тестов с базой данных (PostgreSQL):
```bash
pytest -v tests/api/test_movies_db.py
```

### 📊 Запуск с формированием отчета Allure:
```bash
pytest -v --alluredir=allure-results
allure serve allure-results
```

---

## 🐳 Запуск в Docker

Для запуска автотестов в изолированном контейнере:

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

## 👤 Автор и контакты

- **Автор:** Роман Стахнёв
- **Роль:** Fullstack QA Engineer / QA Automation Engineer (Python)
- **GitHub:** [@madius-ops](https://github.com/madius-ops)
- **Telegram:** [@rst4x51](https://t.me/rst4x51)
- **Email:** [roman.stakhnev.qa@yandex.ru](mailto:roman.stakhnev.qa@yandex.ru)
