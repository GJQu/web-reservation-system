from flask import Blueprint

bp = Blueprint("reservations", __name__)

from app.reservations import routes  # noqa: E402, F401
