import sqlite3 as sl
import streamlit_authenticator as stauth
import yaml
import streamlit as st


class Authenticator:
    def __init__(self):
        # Load the config file
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        auth_config = config["auth"]

        self.conn = sl.connect('auth.db')

        # Check if user table exists, if not create it
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    name TEXT,
                    password TEXT
                );
            """)

        # Get all the usernames and password as json
        with self.conn:
            data = self.conn.execute("""
                SELECT username, name, password FROM user;
            """).fetchall()

            # Convert to json
            users = {}
            for username, name, password in data:
                users[username]= {
                        "name": name,
                        "password": password
                    }
            users = {
                "usernames" : users
            }

        # Create the authenticator
        self.authenticator = stauth.Authenticate(
            users,
            auth_config['cookie']['name'],
            auth_config['cookie']['key'],
            auth_config['cookie']['expiry_days'],
            {"emails": ["alex.and.radchenko@gmail.com"]}
        )

    def check_auth(self):
        self.authenticator._check_cookie()


    def show_signup(self):
        old_users = set(self.authenticator.credentials["usernames"])
        try:
            if self.authenticator.register_user('Sign up', preauthorization=True):
                st.success('User registered successfully')
                new_users = set(self.authenticator.credentials["usernames"])
                new_user = new_users.difference(old_users).pop()
                new_user_creds = self.authenticator.credentials["usernames"][new_user]
                with self.conn:
                    self.conn.execute("""
                        INSERT INTO user (username, name, password) VALUES (?, ?, ?);
                    """, (new_user, new_user_creds["name"], new_user_creds["password"]))
        except Exception as e:
            st.error(e)

    def show_login(self):
        try:
            name, auth_state, password = self.authenticator.login('Login', 'main')
        except Exception as e:
            st.error(e)

    def show_logout(self):
        self.authenticator.logout("Logout", "sidebar")




