from flask import Blueprint

bp = Blueprint("api", __name__)

from app.api.errors import register_error_handlers  # noqa: E402

register_error_handlers(bp)

from app.api import routes  # noqa: E402, F401
