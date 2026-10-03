import click
import sqlite3

from flask import Flask, jsonify, render_template

from .config import load_config, validate_timezone
from .db import get_db, get_schema_version, init_app as init_db_app, init_db
from .routes import tasks_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(load_config())

    if test_config:
        app.config.update(test_config)

    validate_timezone(app.config["APP_TIMEZONE"])
    init_db_app(app)
    app.register_blueprint(tasks_bp)

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

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.cli.command("send-digest")
    @click.option("--to", "to_address", default=None, help="Email de destino.")
    def send_digest_command(to_address):
        """Envia por email o resumo das tarefas abertas (usa SMTP_* e DIGEST_TO)."""
        from .digest import send_digest

        click.echo(send_digest(app, recipient=to_address))

    return app
