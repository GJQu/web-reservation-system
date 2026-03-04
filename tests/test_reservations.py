from app.models import Reservation


class TestWebReservations:
    def test_make_reservation_page_loads(self, auth_client, sample_class):
        response = auth_client.get("/make_reservation")
        assert response.status_code == 200
        assert b"Adult Art Class" in response.data

    def test_submit_reservation(self, auth_client, sample_class):
        response = auth_client.post(
            "/make_reservation",
            data={
                "class_id": sample_class.id,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Reservation successful" in response.data

    def test_manage_reservations_page(self, auth_client, sample_class, db, sample_user):
        reservation = Reservation(user_id=sample_user.id, class_id=sample_class.id)
        db.session.add(reservation)
        db.session.commit()

        response = auth_client.get("/manage_reservation")
        assert response.status_code == 200
        assert b"Adult Art Class" in response.data

    def test_cancel_reservation_web(self, auth_client, sample_class, db, sample_user):
        reservation = Reservation(user_id=sample_user.id, class_id=sample_class.id)
        db.session.add(reservation)
        db.session.commit()

        response = auth_client.post(
            f"/cancel_reservation/{reservation.id}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Reservation cancelled" in response.data

    def test_cannot_cancel_other_users_reservation(self, auth_client, sample_class, db):
        from app.models import User

        other = User(
            username="other",
            email="other@example.com",
            first_name="O",
            last_name="U",
        )
        other.set_password("pw")
        db.session.add(other)
        db.session.commit()

        reservation = Reservation(user_id=other.id, class_id=sample_class.id)
        db.session.add(reservation)
        db.session.commit()

        response = auth_client.post(
            f"/cancel_reservation/{reservation.id}",
            follow_redirects=True,
        )
        assert b"does not belong to you" in response.data
