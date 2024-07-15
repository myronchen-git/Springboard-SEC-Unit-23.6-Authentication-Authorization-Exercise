"""Models for feedback app."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

# ==================================================

db = SQLAlchemy()
bcrypt = Bcrypt()

# --------------------------------------------------


def connect_db(app):
    """Connect to database."""

    with app.app_context():
        db.app = app
        db.init_app(app)
        db.create_all()


class User(db.Model):
    """User model"""

    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    properties = ("username", "password", "email", "first_name", "last_name")

    def __repr__(self):
        """Show info about user."""

        return (
            f"<User("
            f"username='{self.username}', "
            f"password='{self.password}', "
            f"email='{self.email}', "
            f"first_name='{self.first_name}', "
            f"last_name='{self.last_name}')>"
        )

    @classmethod
    def register(cls, form_data_items):
        """
        Saves user and info into database.
        Returns User object if successful, else raises an error.
        """

        form_data = {k: v for k, v in form_data_items
                     if k in cls.properties and v}

        if len(form_data) != len(cls.properties):
            raise KeyError("Missing input(s) for user registration.")

        form_data["password"] = bcrypt.generate_password_hash(
            form_data["password"]).decode("utf8")
        user = cls(**form_data)

        db.session.add(user)
        try:
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Duplicate username or email.")

    @classmethod
    def authenticate(cls, username, password):
        """
        Verifies that username and password are correct.
        Returns User object if valid, else returns False.
        """

        user = db.session.get(User, username)

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
