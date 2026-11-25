from flask import Blueprint, render_template

bp = Blueprint("books", __name__, url_prefix="/books")

@bp.route("/")
def index():
    return render_template("books/index.html")
