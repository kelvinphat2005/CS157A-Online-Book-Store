from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    from .routes import auth, books, orders, staff

    app.register_blueprint(auth.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(staff.bp)

    @app.route("/")
    def index():
        return "Home" # temp

    return app