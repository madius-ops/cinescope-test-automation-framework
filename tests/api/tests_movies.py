from utils.data_generator import DataGenerator


class TestMoviesPositive:

    def test_create_movie(self, movies_api, existing_genre_id):
        payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)

        response = movies_api.create_movie(payload)
        body = response.json()

        assert response.status_code == 201
        assert body["name"] == payload["name"]
        assert body["price"] == payload["price"]
        assert body["location"] == payload["location"]
        assert body["genreId"] == payload["genreId"]
        assert "id" in body

        # cleanup
        movies_api.delete_movie(body["id"], expected_status=200)

    def test_get_movies_list(self, api_manager):
        response = api_manager.movies_api.get_movies()
        body = response.json()

        assert response.status_code == 200
        assert isinstance(body, dict)
        assert "movies" in body
        assert isinstance(body["movies"], list)
        assert "count" in body
        assert "page" in body
        assert "pageSize" in body

    def test_get_movies_filter_by_genre(self, api_manager, created_movie):
        _, payload = created_movie
        target_genre = payload["genreId"]

        response = api_manager.movies_api.get_movies(
            params={"genreId": target_genre, "pageSize": 20}
        )
        body = response.json()["movies"]

        assert response.status_code == 200
        assert all(m["genreId"] == target_genre for m in body)

    def test_get_movies_filter_by_price_range(self, api_manager, created_movie):
        _, payload = created_movie
        price = payload["price"]

        response = api_manager.movies_api.get_movies(
            params={"minPrice": max(1, price - 50), "maxPrice": price + 50, "pageSize": 20}
        )
        body = response.json()["movies"]

        assert response.status_code == 200
        assert all(max(1, price - 50) <= m["price"] <= price + 50 for m in body)

    def test_get_movie_by_id(self, api_manager, created_movie):
        movie_id, payload = created_movie

        body = api_manager.movies_api.get_movie_by_id(movie_id).json()

        assert body["id"] == movie_id
        assert body["name"] == payload["name"]
        assert "reviews" in body

    def test_update_movie(self, movies_api, created_movie):
        movie_id, _ = created_movie
        new_name = DataGenerator.generate_movie_name()

        movies_api.update_movie(movie_id, {"name": new_name})

        body = movies_api.get_movie_by_id(movie_id).json()
        assert body["name"] == new_name

    def test_delete_movie(self, movies_api, existing_genre_id):
        payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
        movie_id = movies_api.create_movie(payload).json()["id"]

        response = movies_api.delete_movie(movie_id)
        assert response.status_code == 200

        # после удаления — 404
        check = movies_api.get_movie_by_id(movie_id, expected_status=404)
        assert check.status_code == 404


class TestMoviesNegative:

    def test_create_movie_without_name(self, movies_api, existing_genre_id):
        payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
        payload.pop("name", None)

        response = movies_api.create_movie(payload, expected_status=400)
        assert response.status_code == 400

    def test_create_movie_with_invalid_genre_id(self, movies_api):
        payload = DataGenerator.generate_movie_payload()
        payload["genreId"] = "not-a-number"

        response = movies_api.create_movie(payload, expected_status=400)
        assert response.status_code == 400

    def test_create_movie_with_invalid_location(self, movies_api, existing_genre_id):
        payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
        payload["location"] = "UNKNOWN"

        response = movies_api.create_movie(payload, expected_status=400)
        assert response.status_code == 400

    def test_create_movie_without_auth(self, api_manager, existing_genre_id):
        """POST /movies требует SUPER_ADMIN — без токена 401."""
        payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)

        response = api_manager.movies_api.create_movie(payload, expected_status=401)
        assert response.status_code == 401

    def test_update_without_auth(self, api_manager, created_movie):
        movie_id, _ = created_movie

        response = api_manager.movies_api.update_movie(
            movie_id, {"name": "Hacked"}, expected_status=401
        )
        assert response.status_code == 401

    def test_delete_without_auth(self, api_manager, created_movie):
        movie_id, _ = created_movie

        response = api_manager.movies_api.delete_movie(movie_id, expected_status=401)
        assert response.status_code == 401

    def test_get_movie_by_nonexistent_id(self, api_manager):
        response = api_manager.movies_api.get_movie_by_id(999_999_999, expected_status=404)
        assert response.status_code == 404

    def test_update_nonexistent_movie(self, movies_api):
        response = movies_api.update_movie(
            999_999_999, {"name": "Ghost"}, expected_status=404
        )
        assert response.status_code == 404

    def test_delete_nonexistent_movie(self, movies_api):
        response = movies_api.delete_movie(999_999_999, expected_status=404)
        assert response.status_code == 404

    def test_get_movies_invalid_page(self, api_manager):
        """page min=1 по схеме — 0 должен дать 400."""
        response = api_manager.movies_api.get_movies(
            params={"page": 0}, expected_status=400
        )
        assert response.status_code == 400

    def test_get_movies_page_size_over_limit(self, api_manager):
        """pageSize max=20 по схеме — 21 должен дать 400."""
        response = api_manager.movies_api.get_movies(
            params={"pageSize": 21}, expected_status=400
        )
        assert response.status_code == 400