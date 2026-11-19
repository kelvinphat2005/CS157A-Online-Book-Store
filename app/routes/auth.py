from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from ..db import get_db

"""
authentication using flask sessions
"""

bp = Blueprint("auth", __name__, url_prefix="/auth")

# decorators
# @login_required -- require user to be logged in for this route
# @admin_required -- require user to be an admin for this route
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "member_id" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "member_id" not in session:
            return redirect(url_for("auth.login"))
        if session.get("role") != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped

# routes
@bp.route("/login", methods=["GET", "POST"])
def login():
    # POST: user submit login info
    if request.method =="POST":
        email = request.form["email"].strip().lower() # TODO: maybe add email validation
        password = request.form["password"]

        cur = get_db().cursor(dictionary=True)

        # get user info from email
        cur.execute("SELECT member_id, name, password_hash, role FROM Members WHERE email = %s",
                    (email,))
        member = cur.fetchone()
        # check if email and password is correct
        if member is None or not check_password_hash(member["password_hash"], password):
            # incorrect
            flash("Invalid email or password")
            return render_template("auth/login.html")

        session.clear()
        session["member_id"] = member["member_id"]
        session["name"] = member["name"]
        session["role"] = member["role"]
        return redirect(url_for("index")) # send to index page

    # GET: else return login page
    return render_template("auth/login.html")

@bp.route("/register", methods=["GET", "POST"])
def register():
    # POST: user submit registration info (name, email, password)
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower() # TODO: maybe add email validation
        password = request.form["password"]

        if not name or not email or not password:
            flash("All fields are required")
            return render_template("auth/register.html")

        db = get_db()
        cur = db.cursor(dictionary=True)
        
        # check if email exists
        cur.execute("SELECT member_id FROM Members WHERE email = %s", (email,))
        if cur.fetchone():
            flash("This email already exists")
            return render_template("auth/register.html")

        # create new account, add to db 
        cur.execute("INSERT INTO Members(name, email, password_hash) VALUES (%s, %s, %s)",
                    (name, email, generate_password_hash(password),))

        db.commit()
        flash("Account created. Please log in.")

        return redirect(url_for("auth.login"))

    # GET: return registration page
    return render_template("auth/register.html")

@bp.route("/logout")
def logout():
    # remove everything stored in the current session
    session.clear()
    flash("You've been logged out")
    return redirect(url_for("index"))