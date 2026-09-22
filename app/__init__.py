import sqlite3

from flask import Flask, jsonify

from .config import load_config, validate_timezone
from .db import get_db, get_schema_version, init_app as init_db_app, init_db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(load_config())

    if test_config:
        app.config.update(test_config)

    validate_timezone(app.config["APP_TIMEZONE"])
    init_db_app(app)

    with app.app_context():
        init_db(app)

    @app.get("/health")
    def health():
        try:
            get_db().execute("SELECT 1").fetchone()
            return jsonify(
                status="ok",
                database="ok",
                schema_version=get_schema_version(),
            )
        except sqlite3.Error:
            return jsonify(status="error", database="unavailable"), 503

    return app
