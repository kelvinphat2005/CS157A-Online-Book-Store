from flask import Blueprint, render_template
from .auth import admin_required

bp = Blueprint("staff", __name__, url_prefix="/staff")

@bp.route("/")
@admin_required
def index():
    return render_template("staff/index.html")
