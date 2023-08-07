from src.authenticator import Authenticator
import streamlit as st
from src.chat_loop import Chat
from src.dbmodels import *
from functions.gmail import link_account
import pandas as pd
import data.core as core
from agents.basic import describe_dataframe


def set_state_defaults():
    """
    Setting the default values for the session state
    and defaults for the app appearance
    """
    st.set_page_config(layout="wide")
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "data" not in st.session_state:
        st.session_state["data"] = {}
    if "data_view" not in st.session_state:
        st.session_state["data_view"] = {"name": None, "columns": None}


def check_authentication(authenticator: Authenticator) -> None:
    """
    Checks the authentication status and shows the appropriate page
    :param authenticator: the authenticator object
    """
    authenticator.check_auth()
    auth_state = st.session_state["authentication_status"]

    # Show the appropriate page based on the authentication status
    if auth_state is None:
        authenticator.show_login()
        return False
    elif auth_state is False:
        authenticator.show_login()
        st.error('Username/password is incorrect')
        return False
    elif auth_state == "signup":
        authenticator.show_signup()
        return False
    elif not st.session_state["authed_user"].approved:
        st.title("Your account is not approved yet.")
        return False

    return True


def show_sidebar(authenticator: Authenticator) -> None:
    """
    Shows all the elements of the sidebar. Also handles file uploading.
    :param authenticator:
    :return:
    """
    authenticator.show_logout()
    st.sidebar.button("Clear chat", on_click=lambda: st.session_state.conversator.reset())
    gmail_linked = st.session_state["authed_user"].gmail_linked()
    text = "Delete Google Account" if gmail_linked else "Link Google Account"
    st.sidebar.button(text, on_click=link_account)


if __name__ == "__main__":
    set_state_defaults()
    authenticator = Authenticator()
    if check_authentication(authenticator):
        st.title("GPT Assistant")
        show_sidebar(authenticator)
        chat = Chat()
        chat.run()
