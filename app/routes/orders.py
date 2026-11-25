from flask import Blueprint, render_template
from .auth import login_required

bp = Blueprint("orders", __name__, url_prefix="/orders")

@bp.route("/")
@login_required
def index():
    # Order queries belong to the team's next feature; this page verifies login access.
    return render_template("orders/index.html")
