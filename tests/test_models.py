from app.models import Reservation, User


class TestUserModel:
    def test_set_and_check_password(self, db):
        user = User(
            username="alice",
            email="alice@example.com",
            first_name="Alice",
            last_name="Smith",
        )
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()

        assert user.check_password("secret123") is True
        assert user.check_password("wrong") is False

    def test_password_hash_is_not_plaintext(self, db):
        user = User(
            username="bob",
            email="bob@example.com",
            first_name="Bob",
            last_name="Jones",
        )
        user.set_password("mypassword")
        assert user.password_hash != "mypassword"

    def test_user_has_timestamps(self, db, sample_user):
        assert sample_user.created_at is not None


class TestStudioClassModel:
    def test_spots_remaining(self, db, sample_class, sample_user):
        assert sample_class.spots_remaining == 10
        assert sample_class.is_full is False

        reservation = Reservation(
            user_id=sample_user.id,
            class_id=sample_class.id,
        )
        db.session.add(reservation)
        db.session.commit()

        assert sample_class.spots_remaining == 9

    def test_full_class(self, db, full_class):
        assert full_class.is_full is True
        assert full_class.spots_remaining == 0

    def test_cancelled_reservations_dont_count(self, db, sample_class, sample_user):
        reservation = Reservation(
            user_id=sample_user.id,
            class_id=sample_class.id,
            status="cancelled",
        )
        db.session.add(reservation)
        db.session.commit()

        assert sample_class.spots_remaining == 10

    def test_time_display(self, db, sample_class):
        assert "5:00 PM" in sample_class.time_display


class TestReservationModel:
    def test_create_reservation(self, db, sample_user, sample_class):
        reservation = Reservation(
            user_id=sample_user.id,
            class_id=sample_class.id,
        )
        db.session.add(reservation)
        db.session.commit()

        assert reservation.status == "confirmed"
        assert reservation.created_at is not None
        assert reservation.cancelled_at is None

    def test_reservation_relationships(self, db, sample_user, sample_class):
        reservation = Reservation(
            user_id=sample_user.id,
            class_id=sample_class.id,
        )
        db.session.add(reservation)
        db.session.commit()

        assert reservation.user.username == "testuser"
        assert reservation.studio_class.name == "Adult Art Class"
