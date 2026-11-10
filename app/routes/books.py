from flask import Blueprint

bp = Blueprint("books", __name__, url_prefix="/books")

@bp.route("/")
def index():
    return "books" # temp