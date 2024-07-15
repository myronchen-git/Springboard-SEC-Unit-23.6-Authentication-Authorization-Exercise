from types import MappingProxyType
from unittest import TestCase

from app import create_app
from models import User, connect_db, db

# ==================================================

app = create_app("feedback_test", testing=True)
app.config['WTF_CSRF_ENABLED'] = False
connect_db(app)

app.app_context().push()

db.drop_all()
db.create_all()

# --------------------------------------------------

data1 = MappingProxyType({"username": "user1", "password": "12345", "repeated_password": "12345",
                          "email": "user1@email.com", "first_name": "asdf", "last_name": "asdf"})


class UserRegistrationTestCase(TestCase):
    """Tests for registration of users."""

    def setUp(self):
        db.session.query(User).delete()

    def tearDown(self):
        db.session.rollback()

    def test_register_user_form(self):
        """Tests displaying the user registration form."""

        # Arrange
        url = "/register"

        # Act
        with app.test_client() as client:
            resp = client.get(url)
            html = resp.get_data(as_text=True)

        # Assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn("<h1>User Registration</h1>", html)
        self.assertIn("Username", html)
        self.assertIn("Password", html)
        self.assertIn("Repeat Password", html)
        self.assertIn("Email", html)
        self.assertIn("First name", html)
        self.assertIn("Last name", html)

    def test_register_user(self):
        """Tests adding a new user."""

        # Arrange
        url = "/register"

        # Act
        with app.test_client() as client:
            resp = client.post(url, data=dict(data1), follow_redirects=True)
            html = resp.get_data(as_text=True)

        # Assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Successfully registered.", html)

        user = db.session.get(User, "user1")
        self.assertEqual(user.username, data1["username"])
        self.assertTrue(user.password)
        self.assertEqual(user.email, data1["email"])
        self.assertEqual(user.first_name, data1["first_name"])
        self.assertEqual(user.last_name, data1["last_name"])

    def test_register_user_with_duplicate_input(self):
        """Tests that registering with an existing input gives an error."""

        # Arrange
        new_properties = {"email": "email@email.com", "username": "user0000"}

        for property, new_value in new_properties.items():
            with self.subTest():
                data2 = dict(data1)
                data2[property] = new_value
                url = "/register"

                with app.test_client() as client:
                    client.post(url, data=dict(data1), follow_redirects=True)

                    with client.session_transaction() as change_session:
                        change_session.clear()

        # Act
                    resp = client.post(url, data=data2, follow_redirects=True)
                    html = resp.get_data(as_text=True)

        # Assert
                self.assertIn("Invalid input", html)

                user_count = db.session.query(User.username).count()
                self.assertEqual(user_count, 1)


class UserLoginTestCase(TestCase):
    """Tests for logging in users."""

    @classmethod
    def setUpClass(cls):
        with app.test_client() as client:
            client.post("/register", data=dict(data1))

    def tearDown(self):
        db.session.rollback()

    def test_user_login_form(self):
        """Tests displaying the user login form."""

        # Arrange
        url = "/login"

        # Act
        with app.test_client() as client:
            resp = client.get(url)
            html = resp.get_data(as_text=True)

        # Assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn("<h1>Login</h1>", html)
        self.assertIn("Username", html)
        self.assertIn("Password", html)

    def test_user_login(self):
        """Tests logging in a user."""

        # Arrange
        data = {"username": data1["username"], "password": data1["password"]}
        url = "/login"

        # Act
        with app.test_client() as client:
            resp = client.post(url, data=data)

        # Assert
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, "/secret")

    def test_user_login_incorrect_username(self):
        """Tests inputting in incorrect info for log in."""

        # Arrange
        attempts = [{"username": "randomuser", "password": data1["password"]},
                    {"username": data1["username"], "password": "random"}]

        for data in attempts:
            with self.subTest():
                url = "/login"

        # Act
                with app.test_client() as client:
                    resp = client.post(url, data=data, follow_redirects=True)
                    html = resp.get_data(as_text=True)

        # Assert
                self.assertIn("Invalid username or password.", html)
                self.assertIn("<h1>Login</h1>", html)
                self.assertIn("Username", html)
                self.assertIn("Password", html)
