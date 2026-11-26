"""Behavior tests for Andy's registration, login, logout, and route access."""
import sqlite3
from urllib.parse import parse_qs, urlsplit
from unittest.mock import MagicMock

import pytest
from mysql.connector import Error, IntegrityError
from werkzeug.security import check_password_hash

from app.routes import auth
from conftest import PASSWORD, register, sign_in, token


@pytest.mark.parametrize("path,heading", [
    ("/", "Every good story"),
    ("/auth/login", "Welcome back."),
    ("/auth/register", "A fresh chapter."),
])
def test_public_pages_render_without_database(client, app, path, heading):
    response = client.get(path)
    assert response.status_code == 200 and heading in response.text
    assert not app.test_connections


def test_registration_creates_customer_with_hash(client, database):
    response = register(client, name="  Andy Reader  ", email="  NEW@EXAMPLE.TEST  ", role="admin")
    assert response.status_code == 302 and response.location == "/auth/login"
    with sqlite3.connect(database) as connection:
        name, email, password_hash, role = connection.execute(
            "SELECT name,email,password_hash,role FROM Members WHERE email=?", ("new@example.test",)
        ).fetchone()
    assert (name, email, role) == ("Andy Reader", "new@example.test", "customer")
    assert password_hash != PASSWORD and check_password_hash(password_hash, PASSWORD)
    with client.session_transaction() as state:
        assert "member_id" not in state  # Signing up does not silently sign in.
    assert "Account created. Please sign in." in client.get(response.location).text


@pytest.mark.parametrize("change,field", [
    ({"name": ""}, "name"), ({"name": " "}, "name"), ({"name": "a" * 101}, "name"),
    ({"email": ""}, "email"), ({"email": "no-at-sign"}, "email"),
    ({"email": "two@@example.test"}, "email"), ({"email": "has space@example.test"}, "email"),
    ({"email": "a" * 250 + "@example.test"}, "email"),
    ({"password": "", "confirm_password": ""}, "password"),
    ({"password": "short", "confirm_password": "short"}, "password"),
    ({"password": "a" * 129, "confirm_password": "a" * 129}, "password"),
    ({"confirm_password": ""}, "confirm_password"),
    ({"confirm_password": "Different123!"}, "confirm_password"),
])
def test_registration_validation(client, app, change, field):
    response = register(client, **change)
    assert response.status_code == 400
    assert f'id="{field}-error"' in response.text
    assert not app.test_connections  # Invalid forms never reach the database.
    assert f'value="{PASSWORD}"' not in response.text


@pytest.mark.parametrize("email", ["customer@example.test", "CUSTOMER@EXAMPLE.TEST", " customer@example.test "])
def test_duplicate_registration_keeps_existing_account(client, database, email):
    response = register(client, email=email)
    assert response.status_code == 409 and "already exists" in response.text
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM Members").fetchone()[0] == 2


def test_successful_login_normalizes_email_and_clears_old_session(client):
    with client.session_transaction() as state:
        state["old_value"] = "remove-me"
    response = sign_in(client, email=" CUSTOMER@EXAMPLE.TEST ")
    assert response.status_code == 302 and response.location == "/"
    with client.session_transaction() as state:
        assert state["member_id"] == 1 and state["role"] == "customer"
        assert state["name"] == "Customer Reader"
        assert "old_value" not in state and "password" not in state and "password_hash" not in state
    home = client.get("/")
    assert "My orders" in home.text and "Sign out" in home.text
    assert 'href="/staff/"' not in home.text


@pytest.mark.parametrize("email,password", [
    ("unknown@example.test", PASSWORD),
    ("customer@example.test", "wrong-password"),
    ("'OR1=1--@example.test", PASSWORD),
])
def test_invalid_login_returns_generic_error(client, email, password):
    response = sign_in(client, email=email, password=password)
    assert response.status_code == 401 and "Invalid email or password." in response.text
    with client.session_transaction() as state:
        assert "member_id" not in state


@pytest.mark.parametrize("changes", [
    {"email": ""}, {"email": "invalid"}, {"email": "a" * 256},
    {"password": ""}, {"password": "x" * 129},
])
def test_login_validation_without_query(client, app, changes):
    response = sign_in(client, **changes)
    assert response.status_code == 400 and not app.test_connections


@pytest.mark.parametrize("path", ["/orders/", "/staff/"])
def test_guest_cannot_open_restricted_url(client, path):
    response = client.get(path)
    assert response.status_code == 302
    parts = urlsplit(response.location)
    assert parts.path == "/auth/login"
    assert parse_qs(parts.query)["next"] == [path]


def test_customer_orders_allowed_staff_forbidden(client):
    sign_in(client)
    assert client.get("/orders/").status_code == 200
    response = client.get("/staff/")
    assert response.status_code == 403 and "is for staff." in response.text


def test_admin_lands_in_staff_workspace(client):
    response = sign_in(client, email="admin@example.test")
    assert response.location == "/staff/"
    assert client.get("/staff/").status_code == 200
    assert client.get("/orders/").status_code == 200
    assert 'href="/staff/"' in client.get("/").text


@pytest.mark.parametrize("path", ["/auth/login", "/auth/register"])
def test_signed_in_member_is_redirected_from_auth_forms(client, path):
    sign_in(client)
    response = client.get(path)
    assert response.status_code == 302 and response.location == "/"


def test_login_returns_to_original_page(client):
    response = sign_in(client, next="/orders/")
    assert response.location == "/orders/"


@pytest.mark.parametrize("destination", [
    "https://example.org", "//example.org/path", r"/\example.org",
    "javascript:alert(1)", "///example.org", "/%2fexample.org",
    "/%5cexample.org", "/\n/example.org", "/%0d%0aLocation:evil",
])
def test_external_or_ambiguous_redirect_is_ignored(client, destination):
    assert sign_in(client, next=destination).location == "/"


@pytest.mark.parametrize("path", ["/auth/login", "/auth/register", "/auth/logout"])
@pytest.mark.parametrize("csrf", ["", "wrong-token", "😈"])
def test_auth_posts_require_valid_csrf(client, path, csrf):
    token(client)
    response = client.post(path, data={"csrf_token": csrf})
    assert response.status_code == 400 and "form has expired" in response.text


def test_csrf_is_bound_to_browser_session(app):
    one, two = app.test_client(), app.test_client()
    one_token = token(one)
    token(two)
    response = two.post("/auth/login", data={
        "email": "customer@example.test", "password": PASSWORD, "csrf_token": one_token,
    })
    assert response.status_code == 400


def test_logout_post_clears_access_and_invalidates_old_token(client):
    old_token = token(client)
    assert client.post("/auth/login", data={
        "email": "customer@example.test", "password": PASSWORD, "csrf_token": old_token,
    }).status_code == 302
    # A form opened before login must not be able to log the new session out.
    assert client.post("/auth/logout", data={"csrf_token": old_token}).status_code == 400
    new_token = token(client, "/")
    assert old_token != new_token
    assert client.post("/auth/logout", data={"csrf_token": new_token}).location == "/auth/login"
    with client.session_transaction() as state:
        assert "member_id" not in state and "role" not in state and "name" not in state
    assert client.get("/orders/").status_code == 302
    assert client.get("/staff/").status_code == 302
    assert client.get("/auth/logout").status_code == 405


def test_customer_then_admin_login_does_not_retain_role(client):
    sign_in(client, email="admin@example.test")
    client.post("/auth/logout", data={"csrf_token": token(client, "/")})
    sign_in(client)
    assert client.get("/staff/").status_code == 403


def test_user_text_is_escaped_and_password_never_refilled(client):
    response = register(client, name='<script>alert("x")</script>', confirm_password="wrong")
    assert response.status_code == 400
    assert '<script>alert("x")</script>' not in response.text
    assert "&lt;script&gt;" in response.text
    assert f'value="{PASSWORD}"' not in response.text


def test_successful_login_closes_database_and_cursor(client, app):
    sign_in(client)
    assert app.test_connections
    assert all(connection.closed for connection in app.test_connections)
    assert all(cursor.closed for connection in app.test_connections for cursor in connection.cursors)
    query, params = app.test_connections[0].queries[0]
    assert "%s" in query and params == ("customer@example.test",)


def test_database_outage_shows_retry_message(client, monkeypatch):
    def unavailable():
        raise Error("Simulated unavailable database")
    monkeypatch.setattr(auth, "get_db", unavailable)
    assert sign_in(client).status_code == 503
    response = register(client)
    assert response.status_code == 503 and "try again shortly" in response.text
    assert "Simulated unavailable database" not in response.text


@pytest.mark.parametrize("code,expected", [(1062, 409), (1048, 503)])
def test_insert_failure_rolls_back_and_closes_cursor(client, monkeypatch, code, expected):
    connection = MagicMock()
    cursor = connection.cursor.return_value
    cursor.fetchone.return_value = None
    cursor.execute.side_effect = [None, IntegrityError("Simulated insert failure", errno=code)]
    monkeypatch.setattr(auth, "get_db", lambda: connection)
    assert register(client).status_code == expected
    connection.rollback.assert_called_once()
    cursor.close.assert_called_once()


@pytest.mark.parametrize("path", ["/", "/auth/login", "/auth/register"])
def test_pages_are_not_cached_and_have_cookie_flags(client, path):
    response = client.get(path)
    assert response.headers["Cache-Control"] == "no-store"
    cookie = response.headers.get("Set-Cookie", "")
    if cookie:
        assert "HttpOnly" in cookie and "SameSite=Lax" in cookie
