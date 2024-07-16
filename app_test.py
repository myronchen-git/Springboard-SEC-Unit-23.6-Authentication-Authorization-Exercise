from types import MappingProxyType
from unittest import TestCase

from flask import session

from app import create_app
from models import Feedback, User, connect_db, db

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
        db.session.query(User).delete()

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
        self.assertEqual(resp.location, f"/users/{data1["username"]}")

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


class UserLogoutTestCase(TestCase):
    """Tests logging out users."""

    def setUp(self):
        db.session.query(User).delete()

    def test_user_logout(self):
        # Arrange
        with app.test_client() as client:
            resp = client.post("/register", data=dict(data1))

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f"/users/{data1["username"]}")
            self.assertIn("username", session)

            url = "/logout"

        # Act
            resp = client.post(url)

        # Assert
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, "/")


class UserProfileTestCase(TestCase):
    """Tests user profile."""

    def setUp(self):
        db.session.query(User).delete()

        with app.test_client() as client:
            client.post("/register", data=dict(data1))

    def test_user_profile_page(self):
        """Tests displaying the user profile webpage."""

        # Arrange
        url = f"/users/{data1["username"]}"

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = data1["username"]

        # Act
            resp = client.get(url)
            html = resp.get_data(as_text=True)

        # Assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn(f"<h2>{data1["username"]}</h2>", html)
        self.assertIn(data1["email"], html)
        self.assertIn(data1["first_name"], html)
        self.assertIn(data1["last_name"], html)
        self.assertIn(f'href="/users/{data1["username"]}/feedback/add"', html)
        self.assertIn(f'"/users/{data1["username"]}/delete"', html)

    def test_user_profile_not_logged_in(self):
        """Tests not displaying the profile webpage if not logged in."""

        # Arrange
        url = f"/users/{data1["username"]}"

        # Act
        with app.test_client() as client:
            resp = client.get(url)

        # Assert
        self.assertEqual(resp.status_code, 401)

    def test_user_profile_with_different_logged_in_user(self):
        """If logged in, users should not be able to see another user's profile."""

        # Arrange
        url = f"/users/{data1["username"]}"

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = "user2"

        # Act
            resp = client.get(url)

        # Assert
        self.assertEqual(resp.status_code, 401)


class DeleteUserTestCase(TestCase):
    """Tests deleting user."""

    def setUp(self):
        db.session.query(User).delete()

        with app.test_client() as client:
            client.post("/register", data=dict(data1))

    def tearDown(self):
        db.session.rollback()

    def test_delete_user(self):
        """Tests deleting a user."""

        # Arrange
        url = f"/users/{data1["username"]}/delete"
        logged_in_user = data1["username"]

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = logged_in_user

        # Act
            resp = client.post(url, follow_redirects=True)

        # Assert
        self.assertEqual(resp.status_code, 200)

        user_count = db.session.query(User).count()
        self.assertEqual(user_count, 0)

    def test_delete_user_(self):
        """Tests deleting a user when it is not the current user."""

        # Arrange
        url = f"/users/{data1["username"]}/delete"
        logged_in_user = "user99"

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = logged_in_user

        # Act
            resp = client.post(url, follow_redirects=True)

        # Assert
        self.assertEqual(resp.status_code, 401)

        user_count = db.session.query(User).count()
        self.assertEqual(user_count, 1)


class AddFeedbackTestCase(TestCase):
    """Tests adding feedback."""

    @classmethod
    def setUpClass(cls):
        db.session.query(User).delete()

        with app.test_client() as client:
            client.post("/register", data=dict(data1))

    def setUp(self):
        db.session.query(Feedback).delete()

    def tearDown(self):
        db.session.rollback()

    def test_add_feedback_form(self):
        """Tests displaying the form to add a feedback."""

        # Arrange
        url = f"/users/{data1["username"]}/feedback/add"

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = data1["username"]

        # Act
            resp = client.get(url)
            html = resp.get_data(as_text=True)

        # Assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn("<h1>Feedback</h1>", html)
        self.assertIn("Title", html)
        self.assertIn("Content", html)
        self.assertIn("<input", html)

    def test_add_feedback(self):
        """Tests adding a feedback."""

        # Arrange
        url = f"/users/{data1["username"]}/feedback/add"
        new_feedback_data = MappingProxyType(
            {"title": "feedback1", "content": "abcd"})

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["username"] = data1["username"]

        # Act
            resp = client.post(url, data=new_feedback_data)

        # Assert
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, f"/users/{data1["username"]}")

        feedback_count = db.session.query(Feedback.id).count()
        self.assertEqual(feedback_count, 1)

        feedback = db.session.query(Feedback).filter_by(
            title=new_feedback_data["title"]).one()
        self.assertEqual(feedback.content, new_feedback_data["content"])
        self.assertEqual(feedback.username, data1["username"])
        self.assertIsInstance(feedback.id, int)
