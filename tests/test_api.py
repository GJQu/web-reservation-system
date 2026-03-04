from app.models import Reservation


class TestClassesAPI:
    def test_list_classes(self, client, sample_class):
        response = client.get("/api/v1/classes")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Adult Art Class"
        assert data["data"][0]["spots_remaining"] == 10
        assert data["error"] is None

    def test_get_class(self, client, sample_class):
        response = client.get(f"/api/v1/classes/{sample_class.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["name"] == "Adult Art Class"

    def test_get_class_not_found(self, client):
        response = client.get("/api/v1/classes/999")
        assert response.status_code == 404
        data = response.get_json()
        assert data["error"]["code"] == "NOT_FOUND"


class TestReservationsAPI:
    def test_create_reservation(self, auth_client, sample_class):
        response = auth_client.post(
            "/api/v1/reservations",
            json={"class_id": sample_class.id},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["status"] == "confirmed"
        assert data["data"]["class_id"] == sample_class.id

    def test_create_reservation_class_full(self, auth_client, full_class):
        response = auth_client.post(
            "/api/v1/reservations",
            json={"class_id": full_class.id},
        )
        assert response.status_code == 409
        data = response.get_json()
        assert data["error"]["code"] == "CLASS_FULL"

    def test_create_duplicate_reservation(
        self, auth_client, sample_class, db, sample_user
    ):
        reservation = Reservation(user_id=sample_user.id, class_id=sample_class.id)
        db.session.add(reservation)
        db.session.commit()

        response = auth_client.post(
            "/api/v1/reservations",
            json={"class_id": sample_class.id},
        )
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "DUPLICATE_RESERVATION"

    def test_list_reservations(self, auth_client, sample_class, db, sample_user):
        reservation = Reservation(user_id=sample_user.id, class_id=sample_class.id)
        db.session.add(reservation)
        db.session.commit()

        response = auth_client.get("/api/v1/reservations")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1

    def test_cancel_reservation(self, auth_client, sample_class, db, sample_user):
        reservation = Reservation(user_id=sample_user.id, class_id=sample_class.id)
        db.session.add(reservation)
        db.session.commit()

        response = auth_client.delete(f"/api/v1/reservations/{reservation.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["status"] == "cancelled"

    def test_cancel_other_users_reservation(self, auth_client, sample_class, db):
        from app.models import User

        other_user = User(
            username="other",
            email="other@example.com",
            first_name="Other",
            last_name="User",
        )
        other_user.set_password("password")
        db.session.add(other_user)
        db.session.commit()

        reservation = Reservation(user_id=other_user.id, class_id=sample_class.id)
        db.session.add(reservation)
        db.session.commit()

        response = auth_client.delete(f"/api/v1/reservations/{reservation.id}")
        assert response.status_code == 403
        assert response.get_json()["error"]["code"] == "FORBIDDEN"

    def test_requires_auth(self, client, sample_class):
        response = client.get("/api/v1/reservations")
        assert response.status_code == 302  # redirect to login


class TestUsersAPI:
    def test_get_current_user(self, auth_client, sample_user):
        response = auth_client.get("/api/v1/users/me")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["username"] == "testuser"
        assert data["data"]["email"] == "test@example.com"

    def test_get_current_user_requires_auth(self, client):
        response = client.get("/api/v1/users/me")
        assert response.status_code == 302
