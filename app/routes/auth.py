"""Kelvin's Flask-session authentication, connected to Andy's form pages."""
from functools import wraps
import re
from urllib.parse import urlsplit

from flask import (
    Blueprint, abort, current_app, flash, redirect, render_template,
    request, session, url_for,
)
from mysql.connector import Error, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import get_db
from ..security import validate_csrf

bp = Blueprint("auth", __name__, url_prefix="/auth")


def _destination():
    """Choose the landing page using the role saved by a successful login."""
    return url_for("staff.index" if session.get("role") == "admin" else "index")


def _safe_next(value):
    """Only return local absolute paths; never redirect to another website."""
    if not value or not value.startswith("/") or value.startswith("//"):
        return ""
    if "\\" in value or any(ord(char) < 32 or ord(char) == 127 for char in value):
        return ""
    parts = urlsplit(value)
    if parts.scheme or parts.netloc:
        return ""
    if any(code in value.lower() for code in ("%2f", "%5c", "%0d", "%0a")):
        return ""
    return value


def login_required(view):
    """Protect the route itself, including requests made by typing its URL."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "member_id" not in session:
            return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "member_id" not in session:
            return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))
        if session.get("role") != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@bp.before_request
def protect_auth_forms():
    # All three forms (including logout) must come from this browser session.
    if request.method == "POST":
        validate_csrf()


@bp.route("/login", methods=["GET", "POST"])
def login():
    if "member_id" in session:
        return redirect(_destination())

    email = request.form.get("email", "").strip().lower()
    next_url = _safe_next(request.form.get("next") or request.args.get("next", ""))
    errors = {}
    status = 200
    if request.method == "POST":
        password = request.form.get("password", "")
        if not email:
            errors["email"] = "Enter your email address."
        elif len(email) > 255 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            errors["email"] = "Enter a valid email address."
        if not password:
            errors["password"] = "Enter your password."
        elif len(password) > 128:
            errors["password"] = "Passwords must be 128 characters or fewer."

        if errors:
            status = 400
        else:
            cursor = None
            try:
                cursor = get_db().cursor(dictionary=True)
                # Keep Kelvin's parameterized SQL and existing Members schema.
                cursor.execute(
                    "SELECT member_id, name, password_hash, role FROM Members WHERE email = %s",
                    (email,),
                )
                member = cursor.fetchone()
                if member is None or not check_password_hash(member["password_hash"], password):
                    errors["form"] = "Invalid email or password."
                    status = 401
                else:
                    # Discard old session values and rotate the CSRF token at login.
                    session.clear()
                    session["member_id"] = member["member_id"]
                    session["name"] = member["name"]
                    session["role"] = member["role"]
                    flash("Welcome back, " + member["name"] + ".", "success")
                    return redirect(next_url or _destination())
            except Error:
                current_app.logger.exception("Could not complete login")
                errors["form"] = "We couldn't sign you in right now. Please try again shortly."
                status = 503
            finally:
                if cursor is not None:
                    cursor.close()

    return render_template(
        "auth/login.html", errors=errors, email=email, next_url=next_url,
    ), status


@bp.route("/register", methods=["GET", "POST"])
def register():
    if "member_id" in session:
        return redirect(_destination())

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    errors = {}
    status = 200
    if request.method == "POST":
        password = request.form.get("password", "")
        confirmation = request.form.get("confirm_password", "")
        if not name:
            errors["name"] = "Enter your full name."
        elif len(name) > 100:
            errors["name"] = "Use 100 characters or fewer."
        if not email or len(email) > 255 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            errors["email"] = "Enter a valid email address."
        if len(password) < 8 or len(password) > 128:
            errors["password"] = "Use between 8 and 128 characters."
        if password != confirmation:
            errors["confirm_password"] = "Your passwords don't match."

        if errors:
            status = 400
        else:
            connection = None
            cursor = None
            try:
                connection = get_db()
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT member_id FROM Members WHERE email = %s", (email,))
                if cursor.fetchone():
                    errors["email"] = "An account with this email already exists. Try signing in."
                    status = 409
                else:
                    # Public registration always creates a customer; ignore any submitted role.
                    cursor.execute(
                        "INSERT INTO Members(name, email, password_hash) VALUES (%s, %s, %s)",
                        (name, email, generate_password_hash(password)),
                    )
                    connection.commit()
                    flash("Account created. Please sign in.", "success")
                    return redirect(url_for("auth.login"))
            except IntegrityError as error:
                if connection is not None:
                    connection.rollback()
                # Handle a second signup that wins a concurrent email check.
                if error.errno == 1062:
                    errors["email"] = "An account with this email already exists. Try signing in."
                    status = 409
                else:
                    current_app.logger.exception("Could not create member")
                    errors["form"] = "We couldn't create your account right now. Please try again shortly."
                    status = 503
            except Error:
                if connection is not None:
                    connection.rollback()
                current_app.logger.exception("Could not create member")
                errors["form"] = "We couldn't create your account right now. Please try again shortly."
                status = 503
            finally:
                if cursor is not None:
                    cursor.close()

    # Passwords are deliberately never passed back to the template.
    return render_template("auth/register.html", errors=errors, name=name, email=email), status


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You've been signed out.", "success")
    return redirect(url_for("auth.login"))
