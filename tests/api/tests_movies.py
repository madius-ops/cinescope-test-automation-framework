from utils.data_generator import DataGenerator


class TestMoviesPositive:

    def test_create_movie(self, super_admin, existing_genre_id):
        payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)

        response = super_admin.api.movies_api.create_movie(payload)
        body = response.json()

        assert response.status_code == 201
        assert body["name"] == payload["name"]
        assert body["price"] == payload["price"]
        assert body["location"] == payload["location"]
        assert body["genreId"] == payload["genreId"]
        assert "id" in body

        # cleanup
        super_admin.api.movies_api.delete_movie(body["id"], expected_status=200)

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

    def test_update_movie(self, super_admin, created_movie):
        movie_id, _ = created_movie
        new_name = DataGenerator.generate_movie_name()

        super_admin.api.movies_api.update_movie(movie_id, {"name": new_name})

        body = super_admin.api.movies_api.get_movie_by_id(movie_id).json()
        assert body["name"] == new_name

    def test_delete_movie(self, super_admin, existing_genre_id):
        payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
        movie_id = super_admin.api.movies_api.create_movie(payload).json()["id"]

        response = super_admin.api.movies_api.delete_movie(movie_id)
        assert response.status_code == 200

        # после удаления — 404
        check = super_admin.api.movies_api.get_movie_by_id(movie_id, expected_status=404)
        assert check.status_code == 404


class TestMoviesNegative:

    def test_create_movie_without_name(self, super_admin, existing_genre_id):
        payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
        payload.pop("name", None)

        response = super_admin.api.movies_api.create_movie(payload, expected_status=400)
        assert response.status_code == 400

    def test_create_movie_with_invalid_genre_id(self, super_admin):
        payload = DataGenerator.generate_movie_payload()
        payload["genreId"] = "not-a-number"

        response = super_admin.api.movies_api.create_movie(payload, expected_status=400)
        assert response.status_code == 400

    def test_create_movie_with_invalid_location(self, super_admin, existing_genre_id):
        payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)
        payload["location"] = "UNKNOWN"

        response = super_admin.api.movies_api.create_movie(payload, expected_status=400)
        assert response.status_code == 400

    def test_create_movie_without_auth(self, api_manager, existing_genre_id):
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

    def test_update_nonexistent_movie(self, super_admin):
        response = super_admin.api.movies_api.update_movie(
            999_999_999, {"name": "Ghost"}, expected_status=404
        )
        assert response.status_code == 404

    def test_delete_nonexistent_movie(self, super_admin):
        response = super_admin.api.movies_api.delete_movie(999_999_999, expected_status=404)
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

    def test_create_movie_with_user_role(self, common_user,existing_genre_id):
        payload = DataGenerator.generate_movie_payload(genre_id=existing_genre_id)

        response = common_user.api.movies_api.create_movie(payload,expected_status=403)
        assert response.status_code == 403