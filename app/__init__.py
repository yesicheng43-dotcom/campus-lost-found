import os
from pathlib import Path

from flask import Flask


def create_app(test_config=None):
    """Create the Flask application used by the local development server."""
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-secret"),
    )

    if test_config is not None:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    app.config.setdefault(
        "DATABASE", str(Path(app.instance_path) / "lost_found.sqlite3")
    )

    from . import db

    db.init_app(app)

    from . import views

    app.register_blueprint(views.bp)

    @app.errorhandler(404)
    def not_found(_error):
        from flask import render_template

        return render_template("404.html"), 404

    return app
