from flask import Blueprint

bp = Blueprint("orders", __name__, url_prefix="/orders")

@bp.route("/")
def index():
    return "orders" # temp