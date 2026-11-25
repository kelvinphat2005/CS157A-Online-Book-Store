"""Isolated auth tests: real SQL execution without requiring a local MySQL server.

Only the test connector adapts MySQL's %s placeholders to SQLite's ? syntax.
The application always imports MySQL Connector/Python and stays on MySQL.
"""
import re
import sqlite3

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app import db as db_module

PASSWORD = "Reading123!"


class TestCursor:
    __test__ = False

    def __init__(self, connection):
        self.connection = connection
        self.raw = connection.raw.cursor()
        self.closed = False

    def execute(self, statement, params=()):
        self.connection.queries.append((statement, params))
        self.raw.execute(statement.replace("%s", "?"), params)

    def fetchone(self):
        row = self.raw.fetchone()
        return dict(row) if row is not None else None

    def close(self):
        self.closed = True
        self.raw.close()


class TestConnection:
    __test__ = False

    def __init__(self, path):
        self.raw = sqlite3.connect(path)
        self.raw.row_factory = sqlite3.Row
        self.cursors = []
        self.queries = []
        self.closed = False

    def cursor(self, dictionary=False):
        assert dictionary, "Application queries should return named columns."
        cursor = TestCursor(self)
        self.cursors.append(cursor)
        return cursor

    def commit(self):
        self.raw.commit()

    def rollback(self):
        self.raw.rollback()

    def close(self):
        self.closed = True
        self.raw.close()


@pytest.fixture(scope="session")
def password_hash():
    return generate_password_hash(PASSWORD)


@pytest.fixture
def database(tmp_path, password_hash):
    path = tmp_path / "members.sqlite"
    with sqlite3.connect(path) as connection:
        connection.execute(
            """CREATE TABLE Members(
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'customer' CHECK(role IN ('customer','admin'))
            )"""
        )
        connection.executemany(
            "INSERT INTO Members(name,email,password_hash,role) VALUES (?,?,?,?)",
            [("Customer Reader", "customer@example.test", password_hash, "customer"),
             ("Staff Reader", "admin@example.test", password_hash, "admin")],
        )
    return path


@pytest.fixture
def app(database, monkeypatch):
    connections = []

    def connect(**settings):
        assert settings["database"] == "bookstore_test"
        assert settings["port"] == 3306
        connection = TestConnection(database)
        connections.append(connection)
        return connection

    monkeypatch.setattr(db_module.mysql.connector, "connect", connect)
    application = create_app({
        "TESTING": True, "SECRET_KEY": "only-used-by-tests",
        "MYSQL_DATABASE": "bookstore_test", "MYSQL_PORT": 3306,
    })
    application.test_connections = connections
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def token(client, path="/auth/login"):
    response = client.get(path)
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    assert match, response.text
    return match.group(1)


def sign_in(client, email="customer@example.test", **extra):
    data = {"email": email, "password": PASSWORD, "csrf_token": token(client)}
    data.update(extra)
    return client.post("/auth/login", data=data)


def register(client, **extra):
    data = {
        "name": "New Reader", "email": "new@example.test",
        "password": PASSWORD, "confirm_password": PASSWORD,
        "csrf_token": token(client, "/auth/register"),
    }
    data.update(extra)
    return client.post("/auth/register", data=data)
