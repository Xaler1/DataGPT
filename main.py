from src.authenticator import Authenticator
import streamlit as st
from src.chat_loop import Chat
from src.dbdriver import DBDriver

if "dbdriver" not in st.session_state:
    st.session_state["dbdriver"] = DBDriver("auth.db")

# Check the authentication status
authenticator = Authenticator()
authenticator.check_auth()
auth_state = st.session_state["authentication_status"]

# Show the appropriate page based on the authentication status
if auth_state is None:
    authenticator.show_login()
elif auth_state is False:
    authenticator.show_login()
    st.error('Username/password is incorrect')
    authenticator.show_signup()
elif auth_state == "signup":
    authenticator.show_signup()
else:
    authenticator.show_logout()
    chat = Chat()
    chat.run()


