from src.authenticator import Authenticator
import streamlit as st
from src.chat_loop import Chat
from src.dbmodels import *
from functions.gmail import link_account
import pandas as pd
from io import StringIO
from agents.data_describer import describe_dataframe

def set_state_defaults():
    st.set_page_config(layout="wide")
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "data" not in st.session_state:
        st.session_state["data"] = {}

def check_authentication(authenticator):
    # Check the authentication status
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

def show_sidebar(authenticator):
    authenticator.show_logout()
    st.sidebar.button("Clear chat", on_click=lambda: st.session_state.conversator.reset())
    gmail_linked = st.session_state["authed_user"].gmail_linked()
    text = "Delete Google Account" if gmail_linked else "Link Google Account"
    st.sidebar.button(text, on_click=link_account)

    expander = st.sidebar.expander("Data")

    # Allow data uploading
    uploaded_file = expander.file_uploader("Upload data", type=["csv"], accept_multiple_files=False, key="data_upload")
    if uploaded_file is not None:
        dataframe = pd.read_csv(uploaded_file)
        name = uploaded_file.name.replace(".csv", "")
        with st.spinner("Processing..."):
            summary = describe_dataframe(name, dataframe)
        st.session_state["data"][name] = {"data": dataframe, "summary": summary, "columns": list(dataframe.columns)}

    col1, col2, col3 = expander.columns(3)
    with col1:
        st.header("Name")
    with col2:
        st.header("Summary")
    with col3:
        st.header("Download")

    for name, data in st.session_state["data"].items():
        with col1:
            st.write(name)
        with col2:
            st.write(data["summary"])
        with col3:
            st.download_button("Download", data["data"].to_csv().encode("utf-8"), f"{name}.csv", "text/csv")


if __name__ == "__main__":
    set_state_defaults()
    authenticator = Authenticator()
    if check_authentication(authenticator):
        st.title("GPT Assistant")
        show_sidebar(authenticator)
        chat = Chat()
        chat.run()



