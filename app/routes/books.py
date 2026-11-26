"""Public book catalog: browse, search, sort, and view one book with its reviews."""
from flask import Blueprint, abort, current_app, render_template, request
from mysql.connector import Error

from ..db import get_db

bp = Blueprint("books", __name__, url_prefix="/books")

# ORDER BY cannot be a %s parameter, so only these fixed clauses are ever used.
SORTS = {
    "title": ("Title (A-Z)", "b.title ASC"),
    "price_low": ("Price: low to high", "b.price ASC, b.title ASC"),
    "price_high": ("Price: high to low", "b.price DESC, b.title ASC"),
    "rating": ("Highest rated", "avg_rating IS NULL, avg_rating DESC, b.title ASC"),
}

MAX_QUERY_LENGTH = 100


def _like_pattern(text):
    """Match text anywhere, treating % and _ typed by the user as plain characters."""
    escaped = text.replace("!", "!!").replace("%", "!%").replace("_", "!_")
    return "%" + escaped + "%"


def _fetch_all(sql, params=()):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()


@bp.route("/")
def index():
    q = request.args.get("q", "").strip()[:MAX_QUERY_LENGTH]
    sort = request.args.get("sort", "title")
    if sort not in SORTS:
        sort = "title"

    sql = """
        SELECT b.book_id, b.title, b.price, b.stock, a.name AS author,
               ROUND(AVG(r.rating), 1) AS avg_rating, COUNT(r.review_id) AS review_count
        FROM Books b
        JOIN Authors a ON a.author_id = b.author_id
        LEFT JOIN Reviews r ON r.book_id = b.book_id
        WHERE b.is_active = TRUE
    """
    params = []
    if q:
        # '!' is the escape character because it means the same thing in MySQL and SQLite.
        sql += " AND (b.title LIKE %s ESCAPE '!' OR a.name LIKE %s ESCAPE '!')"
        pattern = _like_pattern(q)
        params += [pattern, pattern]
    sql += " GROUP BY b.book_id, b.title, b.price, b.stock, a.name"
    sql += " ORDER BY " + SORTS[sort][1]

    try:
        books = _fetch_all(sql, params)
    except Error:
        current_app.logger.exception("Could not load the book catalog")
        return render_template(
            "books/index.html", books=[], q=q, sort=sort, sorts=SORTS, unavailable=True,
        ), 503

    return render_template(
        "books/index.html", books=books, q=q, sort=sort, sorts=SORTS, unavailable=False,
    )


@bp.route("/<int:book_id>")
def detail(book_id):
    try:
        found = _fetch_all(
            """
            SELECT b.book_id, b.title, b.publisher, b.summary, b.price, b.stock,
                   a.name AS author,
                   (SELECT ROUND(AVG(r.rating), 1) FROM Reviews r
                    WHERE r.book_id = b.book_id) AS avg_rating
            FROM Books b
            JOIN Authors a ON a.author_id = b.author_id
            WHERE b.book_id = %s AND b.is_active = TRUE
            """,
            (book_id,),
        )
        if not found:
            abort(404)
        reviews = _fetch_all(
            """
            SELECT r.rating, r.review_text, m.name AS reviewer
            FROM Reviews r
            JOIN Members m ON m.member_id = r.member_id
            WHERE r.book_id = %s
            ORDER BY r.review_id DESC
            """,
            (book_id,),
        )
    except Error:
        current_app.logger.exception("Could not load book %s", book_id)
        return render_template("books/detail.html", book=None, reviews=[], unavailable=True), 503

    return render_template("books/detail.html", book=found[0], reviews=reviews, unavailable=False)
