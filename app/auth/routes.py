from flask import flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user

from app.auth import bp
from app.extensions import db
from app.models import User


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Must provide username.", "error")
            return render_template("login.html"), 403

        if not password:
            flash("Must provide password.", "error")
            return render_template("login.html"), 403

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash("Invalid username and/or password.", "error")
            return render_template("login.html"), 403

        login_user(user)
        return redirect(url_for("main.index"))

    return render_template("login.html")


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")

        if not first_name:
            flash("Must provide first name.", "error")
            return render_template("register.html"), 400

        if not last_name:
            flash("Must provide last name.", "error")
            return render_template("register.html"), 400

        if not username:
            flash("Must provide username.", "error")
            return render_template("register.html"), 400

        if not email:
            flash("Must provide email.", "error")
            return render_template("register.html"), 400

        if not password:
            flash("Must provide password.", "error")
            return render_template("register.html"), 400

        if not confirmation or password != confirmation:
            flash("Passwords do not match.", "error")
            return render_template("register.html"), 400

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")
            return render_template("register.html"), 400

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return render_template("register.html"), 400

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")
