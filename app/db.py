import mysql.connector
from flask import current_app, g

"""
database connection helper
import and use get_db() in any route to get a connection to MySQL
"""

def get_db():
    # g stores data for the current request only
    # open a connection the first time a request needs one, then reuse it
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=current_app.config["MYSQL_HOST"],
            user=current_app.config["MYSQL_USER"],
            password=current_app.config["MYSQL_PASSWORD"],
            database=current_app.config["MYSQL_DATABASE"],
            port=current_app.config.get("MYSQL_PORT", 3306),
            connection_timeout=5,
        )
    return g.db

def close_db(e=None):
    # runs automatically after each request finishes
    # remove the connection from g (if one was opened) and close it
    db = g.pop("db", None)
    if db is not None:
        db.close()
