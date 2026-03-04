class TestRegistration:
    def test_register_success(self, client):
        response = client.post(
            "/register",
            data={
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "new@example.com",
                "password": "password123",
                "confirmation": "password123",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_register_duplicate_username(self, client, sample_user):
        response = client.post(
            "/register",
            data={
                "username": "testuser",
                "first_name": "Another",
                "last_name": "User",
                "email": "another@example.com",
                "password": "password123",
                "confirmation": "password123",
            },
        )
        assert response.status_code == 400

    def test_register_mismatched_passwords(self, client):
        response = client.post(
            "/register",
            data={
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "new@example.com",
                "password": "password123",
                "confirmation": "different",
            },
        )
        assert response.status_code == 400

    def test_register_missing_fields(self, client):
        response = client.post(
            "/register",
            data={
                "username": "newuser",
                "password": "password123",
                "confirmation": "password123",
            },
        )
        assert response.status_code == 400


class TestLogin:
    def test_login_success(self, client, sample_user):
        response = client.post(
            "/login",
            data={
                "username": "testuser",
                "password": "testpassword",
            },
        )
        assert response.status_code == 302  # redirect to home

    def test_login_wrong_password(self, client, sample_user):
        response = client.post(
            "/login",
            data={
                "username": "testuser",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 403

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/login",
            data={
                "username": "nobody",
                "password": "password123",
            },
        )
        assert response.status_code == 403


class TestProtectedRoutes:
    def test_make_reservation_requires_login(self, client):
        response = client.get("/make_reservation")
        assert response.status_code == 302  # redirect to login

    def test_manage_reservation_requires_login(self, client):
        response = client.get("/manage_reservation")
        assert response.status_code == 302
