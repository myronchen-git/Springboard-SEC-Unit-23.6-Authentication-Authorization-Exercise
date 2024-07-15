"""Flask app for feedback."""

from flask import Flask

from models import connect_db
from secret_keys import APP_SECRET_KEY

# ==================================================


def create_app(db_name, testing=False):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://postgres@localhost/{
        db_name}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SECRET_KEY"] = APP_SECRET_KEY

    if not testing:
        app.config["SQLALCHEMY_ECHO"] = True
    else:
        app.config["SQLALCHEMY_ECHO"] = False

        app.config["TESTING"] = True

    # --------------------------------------------------

    return app

# ==================================================


if __name__ == "__main__":
    app = create_app("feedback")
    connect_db(app)
    app.run(debug=True)
