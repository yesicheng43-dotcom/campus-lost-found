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

    from . import views

    app.register_blueprint(views.bp)
    return app
