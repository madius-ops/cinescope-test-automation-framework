import json
import logging
import os
from pydantic import BaseModel
from constants.constants import RED, GREEN, RESET
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager


class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
        pool_kwargs["ssl_context"] = ctx
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            **pool_kwargs
        )


class CustomRequester:
    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, session, base_url):
        self.session = session
        self.session.verify = False

        # Монтируем адаптер для обхода строгого TLS в Python 3.14
        adapter = TLSAdapter()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.base_url = base_url
        self.headers = self.base_headers.copy()
        self.session.headers.update(self.base_headers)
        self.logger = logging.getLogger(__name__)

    def _update_session_headers(self, headers: dict):
        self.session.headers.update(headers)

    def log_request_and_response(self, response):
        """
        Логгирование запросов и ответов. Настройки логгирования описаны в pytest.ini
        Преобразует вывод в curl-like (-H хэдэеры), (-d тело)

        :param response: Объект response получаемый из метода "send_request"
        """
        try:
            request = response.request
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                elif isinstance(request.body, str):
                    body = request.body
                body = f"-d '{body}' \n" if body != '{}' else ''

            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            response_status = response.status_code
            is_success = response.ok
            response_data = response.text
            if not is_success:
                self.logger.info(f"\tRESPONSE:"
                                 f"\nSTATUS_CODE: {RED}{response_status}{RESET}"
                                 f"\nDATA: {RED}{response_data}{RESET}")
        except Exception as e:
            self.logger.info(f"\nLogging went wrong: {type(e)} - {e}")

    def send_request(self, method, endpoint, data=None, params=None, expected_status=200, **kwargs):
        url = f"{self.base_url}{endpoint}"

        # 1. Сначала преобразуем Pydantic-модель в обычный словарь/JSON
        if isinstance(data, BaseModel):
            data = json.loads(data.model_dump_json(exclude_unset=True))

        # 2. И ТОЛЬКО ЗДЕСЬ один раз делаем отправку!
        response = self.session.request(
            method,
            url,
            json=data,
            params=params,
            verify=False,
            **kwargs
        )

        self.log_request_and_response(response)

        if response.status_code != expected_status:
            raise ValueError(
                f"Unexpected status code: {response.status_code}. "
                f"Expected: {expected_status}. "
                f"Response body: {response.text}"
            )

        return response