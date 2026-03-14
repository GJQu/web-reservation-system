"""Seed the database with initial class schedule and a test user."""

import sys
from datetime import time
from pathlib import Path

# Add project root to path so we can import app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models import StudioClass, User  # noqa: E402


def _class(name, day, start, end, capacity=10):
    return {
        "name": name,
        "day": day,
        "start_time": time(*start),
        "end_time": time(*end),
        "capacity": capacity,
    }


CLASSES = [
    _class("Kids Art Class", "Tuesday", (15, 0), (17, 0)),
    _class("Adult Art Class", "Tuesday", (17, 0), (18, 0)),
    _class("Kids Art Class", "Wednesday", (15, 0), (17, 0)),
    _class("Adult Art Class", "Wednesday", (17, 0), (18, 0)),
    _class("Kids Art Class", "Thursday", (15, 0), (17, 0)),
    _class("Adult Art Class", "Thursday", (17, 0), (18, 0)),
    _class("Kids Art Class", "Friday", (15, 0), (17, 0)),
    _class("Adult Art Class", "Friday", (17, 0), (18, 0)),
    _class("Kids Art Class AM", "Saturday", (9, 0), (11, 0), 12),
    _class("Kids Art Class PM", "Saturday", (13, 0), (15, 0), 12),
    _class("Adult Art Class AM", "Saturday", (11, 0), (13, 0)),
    _class("Adult Art Class PM", "Saturday", (15, 0), (17, 0)),
]


def seed():
    """Seed classes and a test user. Run `flask db upgrade` first to create tables."""
    app = create_app("development")

    with app.app_context():
        if StudioClass.query.count() == 0:
            for cls_data in CLASSES:
                db.session.add(StudioClass(**cls_data))
            db.session.commit()
            print(f"Seeded {len(CLASSES)} classes.")
        else:
            print("Classes already seeded, skipping.")

        if User.query.count() == 0:
            user = User(
                username="testuser",
                email="test@example.com",
                first_name="Test",
                last_name="User",
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            print("Created test user (testuser / password123).")
        else:
            print("Users already exist, skipping.")


if __name__ == "__main__":
    seed()
