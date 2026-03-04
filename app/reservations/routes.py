from datetime import datetime, timezone

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Reservation, StudioClass
from app.reservations import bp


@bp.route("/make_reservation", methods=["GET", "POST"])
@login_required
def make_reservation():
    if request.method == "POST":
        class_id = request.form.get("class_id")

        if not class_id:
            flash("Please select a class.", "error")
            return redirect(url_for("reservations.make_reservation"))

        studio_class = db.session.get(StudioClass, int(class_id))
        if not studio_class:
            flash("Class not found.", "error")
            return redirect(url_for("reservations.make_reservation"))

        if studio_class.is_full:
            flash("Sorry, this class is full.", "error")
            return redirect(url_for("reservations.make_reservation"))

        # Check for duplicate reservation
        existing = Reservation.query.filter_by(
            user_id=current_user.id, class_id=int(class_id), status="confirmed"
        ).first()
        if existing:
            flash("You already have a reservation for this class.", "error")
            return redirect(url_for("reservations.make_reservation"))

        reservation = Reservation(
            user_id=current_user.id,
            class_id=int(class_id),
        )
        db.session.add(reservation)
        db.session.commit()

        flash("Reservation successful!")
        return redirect(url_for("reservations.make_reservation"))

    classes = StudioClass.query.order_by(StudioClass.day).all()
    return render_template("make_reservation.html", classes=classes)


@bp.route("/manage_reservation")
@login_required
def manage_reservation():
    reservations = (
        Reservation.query.filter_by(user_id=current_user.id, status="confirmed")
        .join(StudioClass)
        .all()
    )
    return render_template("manage_reservation.html", reservations=reservations)


@bp.route("/cancel_reservation/<int:reservation_id>", methods=["POST"])
@login_required
def cancel_reservation(reservation_id):
    reservation = db.session.get(Reservation, reservation_id)

    if not reservation:
        flash("Reservation not found.", "error")
        return redirect(url_for("reservations.manage_reservation"))

    if reservation.user_id != current_user.id:
        flash("Reservation does not belong to you.", "error")
        return redirect(url_for("reservations.manage_reservation"))

    reservation.status = "cancelled"
    reservation.cancelled_at = datetime.now(timezone.utc)
    db.session.commit()

    flash("Reservation cancelled successfully.")
    return redirect(url_for("reservations.manage_reservation"))
