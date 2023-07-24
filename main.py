from src.authenticator import Authenticator
import streamlit as st
from src.chat_loop import Chat
from src.dbmodels import *

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None

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
elif auth_state == "signup":
    authenticator.show_signup()
elif not st.session_state["authed_user"].approved:
    st.title("Your account is not approved yet.")
else:
    authenticator.show_logout()
    chat = Chat()
    chat.run()


