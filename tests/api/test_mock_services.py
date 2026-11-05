import requests
from pydantic import BaseModel, ConfigDict, Field


# Модель ответа (Pydantic V2)
class WorldClockResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="$id")
    currentDateTime: str
    utcOffset: str
    isDayLightSavingsTime: bool
    dayOfTheWeek: str
    timeZoneName: str
    currentFileTime: int
    ordinalDate: str
    serviceResponse: None = None


class DateTimeRequest(BaseModel):
    currentDateTime: str


class WhatIsTodayResponse(BaseModel):
    message: str


class TestTodayIsHolidayServiceAPI:

    # 1. ТЕСТ С MOCK (через monkeypatch подменяем метод класса)
    def test_what_is_today_BY_MOCK(self, monkeypatch):
        # Жестко говорим тесту: при запросе времени верни 1 января
        fake_time = "2025-01-01T00:00Z"

        response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            json={"currentDateTime": fake_time}
        )

        assert response.status_code == 200
        data = WhatIsTodayResponse(**response.json())
        assert data.message == "Новый год", f"Ожидали 'Новый год', а пришло: {data.message}"

    # 2. ТЕСТ СО STUB (статическая заглушка с 9 мая)
    def test_what_is_today_BY_STUB(self):
        class StubWorldClock:
            currentDateTime = "2025-05-09T00:00Z"

        stub = StubWorldClock()

        response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            json={"currentDateTime": stub.currentDateTime}
        )

        assert response.status_code == 200
        data = WhatIsTodayResponse(**response.json())
        assert data.message == "День Победы", f"Ожидали 'День Победы', а пришло: {data.message}"

    # 3. ТЕСТ С WIREMOCK (через запущенный контейнер Docker)
    @staticmethod
    def setup_wiremock_mapping():
        wiremock_admin_url = "http://localhost:8080/__admin/mappings"
        mapping = {
            "request": {
                "method": "GET",
                "url": "/wire/mock/api/json/utc/now"
            },
            "response": {
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "body": (
                    '{"$id": "1", "currentDateTime": "2025-03-08T00:00Z", '
                    '"utcOffset": "00:00", "isDayLightSavingsTime": false, '
                    '"dayOfTheWeek": "Saturday", "timeZoneName": "UTC", '
                    '"currentFileTime": 1324567890123, "ordinalDate": "2025-67", '
                    '"serviceResponse": null}'
                )
            }
        }
        res = requests.post(wiremock_admin_url, json=mapping)
        assert res.status_code == 201, "Не удалось зарегистрировать маппинг в WireMock"

    def test_what_is_today_BY_WIREMOCK(self):
        self.setup_wiremock_mapping()

        # Идем в Wiremock
        wiremock_response = requests.get("http://localhost:8080/wire/mock/api/json/utc/now")
        assert wiremock_response.status_code == 200
        current_date_time = WorldClockResponse(**wiremock_response.json()).currentDateTime

        # Идем в наш сервис
        response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            json={"currentDateTime": current_date_time}
        )

        assert response.status_code == 200
        data = WhatIsTodayResponse(**response.json())
        assert data.message == "Международный женский день"

    # 4. ТЕСТЫ С FAKE-СЕРВИСОМ (на порту 16001)
    def test_fake_worldclockap(self):
        """Проверяем, что наш Fake-сервер времени работает и отдаёт корректный UTC."""
        res = requests.get(
            "http://127.0.0.1:16001/fake/worldclockapi/api/json/utc/now"
        )
        assert res.status_code == 200, "Fake сервис времени недоступен"

        time_data = WorldClockResponse(**res.json())
        import pytz
        from datetime import datetime

        expected_now = datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ")
        assert time_data.currentDateTime == expected_now, "Дата в Fake не совпала"

    def test_fake_what_is_today(self):
        """Интеграционный прогон: берём время из Fake и кормим его в WhatIsToday."""
        # 1. Запрос в наш Fake-сервис времени
        fake_res = requests.get(
            "http://127.0.0.1:16001/fake/worldclockapi/api/json/utc/now"
        )
        assert fake_res.status_code == 200
        fake_time = WorldClockResponse(**fake_res.json()).currentDateTime

        # 2. Запрос в сервис праздников
        response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            json={"currentDateTime": fake_time},
        )
        assert response.status_code == 200
        data = WhatIsTodayResponse(**response.json())

        # Сегодня обычный рабочий день, праздника нет
        assert data.message == "Сегодня нет праздников в России."