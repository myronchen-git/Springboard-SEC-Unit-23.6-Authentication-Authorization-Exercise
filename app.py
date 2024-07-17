"""Flask app for feedback."""

from flask import Flask, flash, redirect, render_template, session
from werkzeug.exceptions import Unauthorized

from forms import FeedbackForm, LoginUserForm, RegisterUserForm
from models import Feedback, User, connect_db, db
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

        if "username" in session:
            return redirect(f"/users/{session["username"]}")

        form = RegisterUserForm()

        if form.validate_on_submit():
            try:
                user = User.register(form.data.items())
                session["username"] = user.username

                flash("Successfully registered.", "info")
                return redirect(f"/users/{user.username}")
            except (KeyError, ValueError) as e:
                flash(f"Invalid input(s) on registration form.  "
                      f"{str(e)}", "error")

        return render_template("register_user.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login_user():
        """Displays login, and logs in user."""

        if "username" in session:
            return redirect(f"/users/{session["username"]}")

        form = LoginUserForm()

        if form.validate_on_submit():
            user = User.authenticate(form.username.data, form.password.data)

            if user:
                session["username"] = user.username
                return redirect(f"/users/{user.username}")
            else:
                # form.username.errors = ["Invalid username or password."]
                flash("Invalid username or password.")

        return render_template("login_user.html", form=form)

    @app.route("/logout", methods=["POST"])
    def logout_user():
        """Logs out the current user."""

        session.pop("username")
        flash("Logged out.")
        return redirect("/")

    @app.route("/users/<username>")
    def user_profile(username):
        """Show user profile."""

        if username != session.get("username", None):
            raise Unauthorized()

        user = db.get_or_404(User, username)

        return render_template("user_profile.html", user=user, feedbacks=user.feedbacks)

    @app.route("/users/<username>/delete", methods=["POST"])
    def delete_user(username):
        """Deletes a user."""

        if username != session.get("username", None):
            raise Unauthorized()

        user = db.get_or_404(User, username)
        user.delete()
        session.pop("username")

        flash("Delete request sent.")
        return redirect("/")

    @app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
    def add_feedback(username):
        """Shows the form to add a feedback."""

        if username != session.get("username", None):
            raise Unauthorized()

        # Double check that user exists
        db.get_or_404(User, username)

        form = FeedbackForm()

        if form.validate_on_submit():
            Feedback.add(form.title.data, form.content.data, username)
            flash("Successfully added feedback.")
            return redirect(f"/users/{username}")
        else:
            return render_template("add_feedback.html", form=form)

    @app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
    def update_feedback(feedback_id):
        """Updates/edits a feedback."""

        feedback = db.get_or_404(Feedback, feedback_id)

        if feedback.username != session.get("username", None):
            raise Unauthorized()

        form = FeedbackForm(obj=feedback)

        if form.validate_on_submit():
            feedback.update(form.title.data, form.content.data)
            flash("Successfully updated feedback.")
            return redirect(f"/users/{feedback.username}")
        else:
            return render_template("update_feedback.html", form=form)

    @app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
    def delete_feedback(feedback_id):
        """Deletes a feedback."""

        feedback = db.get_or_404(Feedback, feedback_id)
        username = feedback.username

        if username != session.get("username", None):
            raise Unauthorized()

        feedback.delete()

        flash("Delete request sent.")
        return redirect(f"/users/{username}")

    return app

# ==================================================


if __name__ == "__main__":
    app = create_app("feedback")
    connect_db(app)
    app.run(debug=True)
