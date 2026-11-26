"""Behavior tests for the public book catalog and book detail pages."""
import re

import pytest
from mysql.connector import Error

from app.routes import books


def titles(response):
    return re.findall(r'<h2 class="book-card-title">([^<]+)</h2>', response.text)


def test_catalog_lists_active_books_with_author_price_and_rating(client):
    response = client.get("/books/")
    assert response.status_code == 200
    assert "The bookshelves" in response.text
    assert titles(response) == ["100% Fiction_Club", "Garden Paths", "Ocean Notes"]
    assert "Hidden Draft" not in response.text
    assert "Ada Writer" in response.text and "$12.50" in response.text
    assert "4.5" in response.text and "(2 reviews)" in response.text


def test_catalog_shows_stock_levels_and_unreviewed_books(client):
    text = client.get("/books/").text
    assert "Only 3 left" in text and "Out of stock" in text and "In stock" in text
    assert "No reviews yet" in text


@pytest.mark.parametrize("q,expected", [
    ("garden", ["Garden Paths"]),
    ("ben author", ["100% Fiction_Club", "Ocean Notes"]),
    ("hidden", []),
    ("%", ["100% Fiction_Club"]),
    ("_", ["100% Fiction_Club"]),
    ("!", []),
])
def test_catalog_search_matches_title_or_author_literally(client, q, expected):
    response = client.get("/books/", query_string={"q": q})
    assert response.status_code == 200
    assert titles(response) == expected
    if not expected:
        assert "No books match" in response.text


def test_search_text_is_escaped_and_parameterized(client, app):
    response = client.get("/books/", query_string={"q": "<script>x</script>' OR 1=1 --"})
    assert "<script>x</script>" not in response.text
    assert titles(response) == []
    statement, params = app.test_connections[0].queries[-1]
    assert "OR 1=1" not in statement and any("OR 1=1" in p for p in params)


@pytest.mark.parametrize("sort,expected", [
    ("title", ["100% Fiction_Club", "Garden Paths", "Ocean Notes"]),
    ("price_low", ["100% Fiction_Club", "Garden Paths", "Ocean Notes"]),
    ("price_high", ["Ocean Notes", "Garden Paths", "100% Fiction_Club"]),
    ("rating", ["Garden Paths", "Ocean Notes", "100% Fiction_Club"]),
    ("b.price; DROP TABLE Books", ["100% Fiction_Club", "Garden Paths", "Ocean Notes"]),
])
def test_catalog_sorting_uses_only_known_orders(client, app, sort, expected):
    response = client.get("/books/", query_string={"sort": sort})
    assert titles(response) == expected
    assert "DROP" not in app.test_connections[0].queries[-1][0]


def test_detail_shows_book_summary_and_reviews(client):
    response = client.get("/books/1")
    assert response.status_code == 200
    text = response.text
    assert "Garden Paths" in text and "A walk through gardens." in text
    assert "Published by Leaf Press" in text and "$12.50" in text
    assert "Lovely and calm." in text and "Staff Reader" in text
    assert "4.5" in text and "(2 reviews)" in text


def test_detail_escapes_review_text(client):
    text = client.get("/books/2").text
    assert "Too &lt;b&gt;salty&lt;/b&gt; for me." in text


def test_detail_without_reviews_or_publisher(client):
    text = client.get("/books/4").text
    assert "No one has reviewed this book yet." in text
    assert "Published by" not in text


@pytest.mark.parametrize("path", ["/books/3", "/books/999"])
def test_inactive_or_missing_book_is_not_found(client, path):
    response = client.get(path)
    assert response.status_code == 404 and "isn't on our shelves" in response.text


def test_catalog_closes_connection_and_cursors(client, app):
    client.get("/books/1")
    connection = app.test_connections[0]
    assert connection.closed and all(cursor.closed for cursor in connection.cursors)


@pytest.mark.parametrize("path,message", [
    ("/books/", "couldn't load the catalog"),
    ("/books/1", "couldn't load this book"),
])
def test_database_outage_shows_retry_message(client, monkeypatch, path, message):
    def unavailable():
        raise Error("database offline")

    monkeypatch.setattr(books, "get_db", unavailable)
    response = client.get(path)
    assert response.status_code == 503 and message in response.text
