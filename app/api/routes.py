from datetime import datetime, timezone

from flask import jsonify, request
from flask_login import current_user, login_required

from app.api import bp
from app.api.errors import (
    ClassFullError,
    DuplicateReservationError,
    ForbiddenError,
    NotFoundError,
)
from app.api.schemas import (
    ClassSchema,
    ReservationCreateSchema,
    ReservationSchema,
    UserSchema,
)
from app.extensions import db
from app.models import Reservation, StudioClass

class_schema = ClassSchema()
classes_schema = ClassSchema(many=True)
reservation_schema = ReservationSchema()
reservations_schema = ReservationSchema(many=True)
reservation_create_schema = ReservationCreateSchema()
user_schema = UserSchema()


def api_response(data, status_code=200):
    return jsonify({"data": data, "error": None}), status_code


@bp.route("/classes")
def list_classes():
    classes = StudioClass.query.order_by(StudioClass.day).all()
    return api_response(classes_schema.dump(classes))


@bp.route("/classes/<int:class_id>")
def get_class(class_id):
    studio_class = db.session.get(StudioClass, class_id)
    if not studio_class:
        raise NotFoundError("Class")
    return api_response(class_schema.dump(studio_class))


@bp.route("/reservations")
@login_required
def list_reservations():
    reservations = Reservation.query.filter_by(
        user_id=current_user.id, status="confirmed"
    ).all()
    return api_response(reservations_schema.dump(reservations))


@bp.route("/reservations", methods=["POST"])
@login_required
def create_reservation():
    errors = reservation_create_schema.validate(request.get_json() or {})
    if errors:
        return jsonify(
            {
                "data": None,
                "error": {"code": "VALIDATION_ERROR", "message": str(errors)},
            }
        ), 400

    data = reservation_create_schema.load(request.get_json())
    class_id = data["class_id"]

    studio_class = db.session.get(StudioClass, class_id)
    if not studio_class:
        raise NotFoundError("Class")

    if studio_class.is_full:
        raise ClassFullError()

    existing = Reservation.query.filter_by(
        user_id=current_user.id, class_id=class_id, status="confirmed"
    ).first()
    if existing:
        raise DuplicateReservationError()

    reservation = Reservation(user_id=current_user.id, class_id=class_id)
    db.session.add(reservation)
    db.session.commit()

    return api_response(reservation_schema.dump(reservation), 201)


@bp.route("/reservations/<int:reservation_id>", methods=["DELETE"])
@login_required
def cancel_reservation(reservation_id):
    reservation = db.session.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError("Reservation")

    if reservation.user_id != current_user.id:
        raise ForbiddenError()

    reservation.status = "cancelled"
    reservation.cancelled_at = datetime.now(timezone.utc)
    db.session.commit()

    return api_response(reservation_schema.dump(reservation))


@bp.route("/users/me")
@login_required
def get_current_user():
    return api_response(user_schema.dump(current_user))
