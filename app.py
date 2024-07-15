"""Flask app for feedback."""

from flask import Flask, flash, redirect, render_template

from forms import registerUserForm
from models import User, connect_db, db
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

    @app.route("/")
    def display_root():
        """Redirects to /register."""

        return redirect("/register")

    @app.route("/register", methods=["GET", "POST"])
    def register_user():
        """Displays the form to register a user, and registers a user."""

        form = registerUserForm()

        if form.validate_on_submit():
            try:
                User.register(form.data.items())

                flash("Successfully registered.", "info")
                return redirect("/secret")
            except (KeyError, ValueError) as e:
                flash(f"Invalid input(s) on registration form.  "
                      f"{str(e)}", "error")

        return render_template("register_user.html", form=form)

    @app.route("/secret")
    def secret():
        return render_template("secret.html")

    return app

# ==================================================


if __name__ == "__main__":
    app = create_app("feedback")
    connect_db(app)
    app.run(debug=True)
