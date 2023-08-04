import streamlit_authenticator as stauth
import yaml
import streamlit as st
from src.dbmodels import User
from peewee import DoesNotExist


class Authenticator:
    """
    The authenticator class. Handles all the authentication logic.
    """

    def __init__(self):
        # Load the config file
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        auth_config = config["auth"]

        # Convert to json
        users = {}
        for user in User.select():
            users[user.username] = {
                "name": user.name,
                "password": user.password
            }
        users = {
            "usernames": users
        }

        # Create the library authenticator
        self.authenticator = stauth.Authenticate(
            users,
            auth_config['cookie']['name'],
            auth_config['cookie']['key'],
            auth_config['cookie']['expiry_days'],
            {"emails": []}
        )

    def check_auth(self) -> None:
        """
        Checks for an authentication cookie. Then checks if the user is in the database.
        If not, the cookie is deleted.
        """
        self.authenticator._check_cookie()
        if st.session_state["authentication_status"] is True:
            try:
                st.session_state["authed_user"] = User.get(User.username == st.session_state["username"])
            except DoesNotExist:
                st.session_state["authentication_status"] = None
                st.session_state["username"] = None
                self.authenticator.cookie_manager.delete(self.authenticator.cookie_name)

    def show_signup(self) -> None:
        """
        Shows the signup page and upon signup captures the new user's
        credentials and adds them to the database.
        """
        old_users = set(self.authenticator.credentials["usernames"])
        try:
            if self.authenticator.register_user('Sign up', preauthorization=False):
                st.success('User registered successfully')
                new_users = set(self.authenticator.credentials["usernames"])
                new_username = new_users.difference(old_users).pop()
                new_user_creds = self.authenticator.credentials["usernames"][new_username]
                new_user = User.create(username=new_username,
                                       name=new_user_creds["name"],
                                       email=new_user_creds["email"],
                                       password=new_user_creds["password"])
                new_user.save()
                st.session_state["authentication_status"] = None
                st.experimental_rerun()
        except Exception as e:
            st.error(e)

        st.button("Login", on_click=lambda: st.session_state.__setitem__("authentication_status", None))

    def show_login(self):
        """
        Shows the login page and upon login sets the session state to the logged in user.
        """
        try:
            name, auth_state, username = self.authenticator.login('Login', 'main')
            if auth_state:
                user = User.get(User.username == username)
                st.session_state["user"] = user
        except Exception as e:
            st.error(e)
        st.button("Sign up", on_click=lambda: st.session_state.__setitem__("authentication_status", "signup"))

    def show_logout(self):
        """
        Shows the logout button and upon logout clears the session state.
        :return:
        """
        self.authenticator.logout("Logout", "sidebar")
        st.session_state["user"] = None
