import pytest
from datetime import time

from app import create_app
from app.extensions import db as _db
from app.models import StudioClass, User


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_user(db):
    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
    )
    user.set_password("testpassword")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_class(db):
    cls = StudioClass(
        name="Adult Art Class",
        day="Tuesday",
        start_time=time(17, 0),
        end_time=time(18, 0),
        capacity=10,
    )
    db.session.add(cls)
    db.session.commit()
    return cls


@pytest.fixture
def full_class(db):
    cls = StudioClass(
        name="Full Class",
        day="Wednesday",
        start_time=time(15, 0),
        end_time=time(17, 0),
        capacity=0,
    )
    db.session.add(cls)
    db.session.commit()
    return cls


@pytest.fixture
def auth_client(client, sample_user):
    """A test client that is already logged in."""
    client.post("/login", data={
        "username": "testuser",
        "password": "testpassword",
    })
    return client
