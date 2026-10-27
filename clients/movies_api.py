from custom_requester.custom_requester import CustomRequester
from config.base_urls import MOVIES_BASE_URL

MOVIES = '/movies'


class MoviesApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=MOVIES_BASE_URL)

    def create_movie(self, payload, expected_status=201, **kwargs):
        return self.send_request("POST", MOVIES, data=payload,
                                 expected_status=expected_status, **kwargs)

    def get_movies(self, params=None, expected_status=200, **kwargs):
        return self.send_request("GET", MOVIES, params=params,
                                 expected_status=expected_status, **kwargs)

    def get_movie_by_id(self, movie_id, expected_status=200, **kwargs):
        return self.send_request("GET", f"{MOVIES}/{movie_id}",
                                 expected_status=expected_status, **kwargs)

    def update_movie(self, movie_id, payload, expected_status=200, **kwargs):
        return self.send_request("PATCH", f"{MOVIES}/{movie_id}", data=payload,
                                 expected_status=expected_status, **kwargs)

    def delete_movie(self, movie_id, expected_status=200, **kwargs):  # ← 200, не 204
        return self.send_request("DELETE", f"{MOVIES}/{movie_id}",
                                 expected_status=expected_status, **kwargs)