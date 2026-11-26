from flask import Flask, render_template

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object("config")
    if test_config is not None:
        app.config.update(test_config)

    from . import db, security
    app.teardown_appcontext(db.close_db)
    security.init_app(app)

    from .routes import auth, books, orders, staff

    app.register_blueprint(auth.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(staff.bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.errorhandler(400)
    def bad_request(error):
        return render_template("errors/400.html", message=error.description), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.after_request
    def avoid_cached_account_pages(response):
        # Signed-out browsers must fetch account pages again rather than cache them.
        if response.mimetype == "text/html":
            response.headers["Cache-Control"] = "no-store"
        return response

    return app
