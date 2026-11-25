"""Small, dependency-free CSRF helper for this project's HTML forms."""
from secrets import compare_digest, token_urlsafe

from flask import abort, request, session


def csrf_token():
    """Templates call this to add the current session's hidden form token."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = token_urlsafe(32)
    return session["_csrf_token"]


def validate_csrf():
    expected = session.get("_csrf_token", "")
    supplied = request.form.get("csrf_token", "")
    if not expected or not supplied.isascii() or not compare_digest(expected, supplied):
        abort(400, description="This form has expired. Reload the page and try again.")


def init_app(app):
    app.jinja_env.globals["csrf_token"] = csrf_token
