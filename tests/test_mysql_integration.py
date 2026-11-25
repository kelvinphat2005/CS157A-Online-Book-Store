"""Opt-in tests against a running MySQL/MariaDB server and the real connector.

Run with BOOKSTORE_TEST_MYSQL=1 and the MYSQL_* connection variables set.
The test creates its own random database, imports Schema.sql there, and drops
only that database when finished. Never reinitializes your bookstore database.
"""
import os
from pathlib import Path
from uuid import uuid4
import re

import mysql.connector
import pytest
from werkzeug.security import check_password_hash, generate_password_hash

from app import create_app
from conftest import PASSWORD, register, sign_in, token

pytestmark = pytest.mark.skipif(
    os.environ.get("BOOKSTORE_TEST_MYSQL") != "1",
    reason="Set BOOKSTORE_TEST_MYSQL=1 to run against your local MySQL server.",
)


@pytest.fixture(scope="module")
def mysql_app():
    settings = {
        "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
    }
    # Generated locally from a fixed prefix and hex UUID, never from user input.
    database = "bookstore_auth_test_" + uuid4().hex
    connection = mysql.connector.connect(**settings)
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE {database}")
    cursor.execute(f"USE {database}")
    try:
        source = (Path(__file__).resolve().parents[1] / "Schema.sql").read_text()
        source = re.sub(r"(?m)^--.*$", "", source)
        for statement in source.split(";"):
            if statement.strip():
                cursor.execute(statement)
        for name, email, role in [
            ("Customer Reader", "customer@example.test", "customer"),
            ("Staff Reader", "admin@example.test", "admin"),
        ]:
            cursor.execute(
                "INSERT INTO Members(name,email,password_hash,role) VALUES (%s,%s,%s,%s)",
                (name, email, generate_password_hash(PASSWORD), role),
            )
        connection.commit()
        app = create_app({
            "TESTING": True, "SECRET_KEY": "test-only-live-db-key",
            "MYSQL_HOST": settings["host"], "MYSQL_PORT": settings["port"],
            "MYSQL_USER": settings["user"], "MYSQL_PASSWORD": settings["password"],
            "MYSQL_DATABASE": database,
        })
        yield app
    finally:
        cursor.execute(f"DROP DATABASE {database}")
        cursor.close()
        connection.close()


@pytest.fixture
def live_client(mysql_app):
    return mysql_app.test_client()


def test_mysql_registration_and_stored_hash(live_client, mysql_app):
    assert register(live_client, role="admin").status_code == 302
    config = mysql_app.config
    connection = mysql.connector.connect(
        host=config["MYSQL_HOST"], port=config["MYSQL_PORT"], user=config["MYSQL_USER"],
        password=config["MYSQL_PASSWORD"], database=config["MYSQL_DATABASE"],
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Members WHERE email=%s", ("new@example.test",))
    row = cursor.fetchone()
    assert row["role"] == "customer"
    assert check_password_hash(row["password_hash"], PASSWORD)
    assert row["password_hash"] != PASSWORD
    cursor.close()
    connection.close()


def test_mysql_duplicate_email(live_client):
    response = register(live_client, email="CUSTOMER@EXAMPLE.TEST")
    assert response.status_code == 409 and "already exists" in response.text


def test_mysql_customer_login_and_restrictions(live_client):
    assert sign_in(live_client).status_code == 302
    assert live_client.get("/orders/").status_code == 200
    assert live_client.get("/staff/").status_code == 403


def test_mysql_admin_login(live_client):
    assert sign_in(live_client, email="admin@example.test").location == "/staff/"
    assert live_client.get("/staff/").status_code == 200


def test_mysql_wrong_password(live_client):
    assert sign_in(live_client, password="WrongPassword!").status_code == 401
    assert live_client.get("/orders/").status_code == 302


def test_mysql_logout_revokes_page_access(live_client):
    sign_in(live_client)
    response = live_client.post("/auth/logout", data={"csrf_token": token(live_client, "/")})
    assert response.status_code == 302
    assert live_client.get("/orders/").status_code == 302


def test_mysql_parameterized_login(live_client):
    assert sign_in(live_client, email="'OR1=1--@example.test").status_code == 401


def test_mysql_full_signup_login_logout(live_client):
    assert register(live_client, email="roundtrip@example.test", name="Round Trip").status_code == 302
    assert sign_in(live_client, email="roundtrip@example.test").status_code == 302
    assert "Round Trip" in live_client.get("/orders/").text
    assert live_client.post(
        "/auth/logout", data={"csrf_token": token(live_client, "/")},
    ).status_code == 302
    assert live_client.get("/orders/").status_code == 302
