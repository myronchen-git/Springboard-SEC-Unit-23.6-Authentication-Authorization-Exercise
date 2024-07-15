from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import EqualTo, InputRequired, Length

# ==================================================


class registerUserForm(FlaskForm):
    """Form to register a user."""

    username = StringField("Username", validators=[
        InputRequired(message="Username is required."),
        Length(3, 20, "Username needs to be 3-20 characters long, inclusive.")])

    password = PasswordField("Password", validators=[
        InputRequired(message="Password is required.")])

    repeated_password = PasswordField("Repeat Password", validators=[
        InputRequired("Repeated password is required."),
        EqualTo("password", message="Password must match.")])

    email = EmailField("Email", validators=[
        InputRequired(message="Email is required."),
        Length(max=50, message="Email can be at most 50 characters long.")])

    first_name = StringField("First name", validators=[
        InputRequired(message="First name is required."),
        Length(2, 30, "First name needs to be 2-30 characters long, inclusive.")])

    last_name = StringField("Last name", validators=[
        InputRequired(message="Last name is required."),
        Length(2, 30, "Last name needs to be 2-30 characters long, inclusive.")])
