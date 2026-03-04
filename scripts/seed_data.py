"""Seed the database with initial class schedule and a test user."""

import sys
from datetime import time
from pathlib import Path

# Add project root to path so we can import app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.extensions import db
from app.models import StudioClass, User


CLASSES = [
    # Tuesday
    {"name": "Kids Art Class", "day": "Tuesday", "start_time": time(15, 0), "end_time": time(17, 0), "capacity": 10},
    {"name": "Adult Art Class", "day": "Tuesday", "start_time": time(17, 0), "end_time": time(18, 0), "capacity": 10},
    # Wednesday
    {"name": "Kids Art Class", "day": "Wednesday", "start_time": time(15, 0), "end_time": time(17, 0), "capacity": 10},
    {"name": "Adult Art Class", "day": "Wednesday", "start_time": time(17, 0), "end_time": time(18, 0), "capacity": 10},
    # Thursday
    {"name": "Kids Art Class", "day": "Thursday", "start_time": time(15, 0), "end_time": time(17, 0), "capacity": 10},
    {"name": "Adult Art Class", "day": "Thursday", "start_time": time(17, 0), "end_time": time(18, 0), "capacity": 10},
    # Friday
    {"name": "Kids Art Class", "day": "Friday", "start_time": time(15, 0), "end_time": time(17, 0), "capacity": 10},
    {"name": "Adult Art Class", "day": "Friday", "start_time": time(17, 0), "end_time": time(18, 0), "capacity": 10},
    # Saturday
    {"name": "Kids Art Class AM", "day": "Saturday", "start_time": time(9, 0), "end_time": time(11, 0), "capacity": 12},
    {"name": "Kids Art Class PM", "day": "Saturday", "start_time": time(13, 0), "end_time": time(15, 0), "capacity": 12},
    {"name": "Adult Art Class AM", "day": "Saturday", "start_time": time(11, 0), "end_time": time(13, 0), "capacity": 10},
    {"name": "Adult Art Class PM", "day": "Saturday", "start_time": time(15, 0), "end_time": time(17, 0), "capacity": 10},
]


def seed():
    app = create_app("development")

    with app.app_context():
        db.create_all()

        # Seed classes if table is empty
        if StudioClass.query.count() == 0:
            for cls_data in CLASSES:
                db.session.add(StudioClass(**cls_data))
            db.session.commit()
            print(f"Seeded {len(CLASSES)} classes.")
        else:
            print("Classes already seeded, skipping.")

        # Create a test user if none exist
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
