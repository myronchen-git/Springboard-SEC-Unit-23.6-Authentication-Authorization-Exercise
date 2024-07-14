"""Models for feedback app."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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
