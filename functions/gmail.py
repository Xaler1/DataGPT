import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from requests import HTTPError
from src.gpt_function import gpt_function
import os
from streamlit.components.v1 import html
import urllib.parse
import threading
import socket
import json
from src.dbmodels import User
import yaml

_SCOPES = [
    "https://mail.google.com/"
]


def open_page(url: str):
    """
    Opens a new page in the browser.
    :param url: the url to open
    """
    open_script = """
        <script type="text/javascript">
            window.open('%s', '_blank').focus();
        </script>
    """ % (url)
    html(open_script)


def retrieve_creds(flow: InstalledAppFlow, state: str, auth_port: int, user: User):
    """
    Runs a gmail authentication server to retrieve the credentials after the user signs in.
    :param flow: the authentication flow object
    :param state: the state id of the authentication
    :param auth_port: the port to run the authentication server on
    :param user: the user to save the credentials to
    """
    creds = flow.run_local_server(port=auth_port, open_browser=False, state=state)
    # Save the credentials for the next run
    user.gmail_token = creds.to_json()
    user.save()
    st.experimental_rerun()


def retrieve_timeout(flow: InstalledAppFlow, state: str, auth_port: int, user: User, timeout=500):
    """
    Used to timeout the process of retrieving the credentials.
    :param flow: the authentication flow object
    :param state: the state id of the authentication
    :param auth_port: the port to run the authentication server on
    :param user: the user to save the credentials to
    :param timeout: the timeout in seconds
    """
    thread = threading.Thread(target=retrieve_creds, args=(flow, state, auth_port, user))
    thread.start()
    thread.join(timeout=timeout)


def link_account():
    """
    Links the user's gmail account to the app.
    Runs the authentication process in a new thread.
    """
    if st.session_state["authed_user"].gmail_linked():
        st.session_state["authed_user"].gmail_token = None
        st.session_state["authed_user"].save()
        st.experimental_rerun()

    config = yaml.safe_load(open("config.yaml", "r"))["gmail"]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        for port in range(8502, 8600):
            if s.connect_ex(('localhost', port)) != 0:
                auth_port = port
                break
    print("Port", auth_port)
    flow = InstalledAppFlow.from_client_secrets_file('secret/credentials.json', _SCOPES)
    url, state = flow.authorization_url()
    redirect = urllib.parse.quote_plus(config['auth_redir'])
    url = url + "&redirect_uri=" + redirect
    open_page(url)
    user = st.session_state["authed_user"]
    thread = threading.Thread(target=retrieve_timeout, args=(flow, state, auth_port, user))
    thread.start()


def _init_services():
    """
    Initializes the Gmail service.
    :return: the Gmail service
    """

    creds = None
    # Import credentials or create new ones
    if st.session_state["authed_user"].gmail_token is not None:
        user = st.session_state["authed_user"]
        token = json.loads(user.gmail_token)
        print(token)
        creds = Credentials.from_authorized_user_info(token, _SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            st.session_state["authed_user"].gmail_token = creds.to_json()
            st.session_state["authed_user"].save()
        else:
            return None

    if "service" not in st.session_state:
        st.session_state.service = build('gmail', 'v1', credentials=creds)
    return st.session_state.service


def get_email(service, email_id) -> dict:
    """
    Gets the email with the given id.
    Parsed into a dictionary.
    :param service: the Gmail service
    :param email_id: the id of the email
    :return: the email as a dictionary
    """
    msg = service.users().messages().get(userId="me", id=email_id).execute()
    subject = ""
    sender = ""
    date = ""
    for header in msg["payload"]["headers"]:
        if header["name"] == "Subject":
            subject = header["value"]
        elif header["name"] == "From":
            sender = header["value"]
        elif header["name"] == "Date":
            date = header["value"]

    body = msg["payload"]["body"]
    if "size" in body and body["size"] == 0:
        if "size" in msg["payload"]["parts"][0]["body"] and msg["payload"]["parts"][0]["body"]["size"] == 0:
            body = msg["payload"]["parts"][0]["parts"][0]["body"]["data"]
        else:
            body = msg["payload"]["parts"][0]["body"]["data"]
    else:
        body = body["data"]

    body = base64.urlsafe_b64decode(body).decode("utf-8")
    return {"subject": subject,
            "sender": sender,
            "date": date,
            "body": body,
            "labels": msg["labelIds"],
            "id": email_id
            }


@gpt_function
def get_user_email():
    """
    Useful for getting the email of the user you are talking to.
    """

    service = _init_services()
    if service is None:
        return {"outcome": "You have not linked a google account yet. Please link one in the sidebar."}

    user_info = service.users().getProfile(userId="me").execute()
    return {"email": user_info["emailAddress"]}


@gpt_function
def send_email(recipient_email: str, subject: str, body: str):
    """
    Useful for sending an email from a gmail account. Must absolutely never be used unless explicitly told to "send" by the user
    Always ask for confirmation before sending.

    :param recipient_email: the email address of the recipient
    :param subject: the subject of the email
    :param body: the body of the email. Must be neat and formatted as html.
    """

    service = _init_services()
    if service is None:
        return {"outcome": "You have not linked a google account yet. Please link one in the sidebar."}

    # Write markdown email
    message = MIMEText(body, "html")
    message["to"] = recipient_email
    message["subject"] = subject
    create_message = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}

    try:
        message = (service.users().messages().send(userId="me", body=create_message).execute())
        return {"outcome": f'sent message to {message} Message Id: {message["id"]}'}
    except HTTPError as error:
        return {"outcome": f'An error occurred: {error}'}


@gpt_function
def get_email_by_id(email_id: str):
    """
    Useful for getting the full text of an email by its id.
    :param email_id: the id of the email
    """

    service = _init_services()
    if service is None:
        return {"outcome": "You have not linked a google account yet. Please link one in the sidebar."}

    return get_email(service, email_id)


@gpt_function
def reply_to_email(body: str, email_id: str):
    """
    Useful for sending a response to an email.
    :param body: the body of the email. Must be neat and formatted as html.
    :param email_id: the id of the email to respond to
    """

    service = _init_services()
    if service is None:
        return {"outcome": "You have not linked a google account yet. Please link one in the sidebar."}

    msg = service.users().messages().get(userId="me", id=email_id).execute()
    email = get_email(service, email_id)

    message = MIMEText(body, "html")
    message["to"] = email["sender"]
    message["subject"] = f"Re: {email['subject']}"
    message["In-Reply-To"] = email["id"]
    message["References"] = email["id"]
    create_message = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode(), "threadId": msg["threadId"]}

    try:
        message = (service.users().messages().send(userId="me", body=create_message).execute())
        return {"outcome": f'sent message to {message} Message Id: {message["id"]}'}
    except HTTPError as error:
        return {"outcome": f'An error occurred: {error}'}


@gpt_function
def search_email(query: str, max_results: int = 5):
    """
    Useful for searching for emails in the user's inbox.
    :param query: the query to search for. Use the same search syntax as you would in gmail. DO NOT invent or assume emails.
    :param max_results: the maximum number of results to return, optional integer
    :return: a list of emails
    """

    service = _init_services()
    if service is None:
        return {"outcome": "You have not linked a google account yet. Please link one in the sidebar."}

    results = service.users().messages().list(userId="me", q=query).execute()
    messages = results.get("messages", [])

    if not messages:
        return {"outcome": "No messages found."}

    formatted_messages = {"messages": []}
    for message in messages[:max_results]:
        msg = service.users().messages().get(userId="me", id=message["id"]).execute()
        subject = ""
        sender = ""
        date = ""
        for header in msg["payload"]["headers"]:
            if header["name"] == "Subject":
                subject = header["value"]
            elif header["name"] == "From":
                sender = header["value"]
            elif header["name"] == "Date":
                date = header["value"]

        snippet = msg["snippet"]
        formatted_messages["messages"].append(
            {
                "subject": subject,
                "sender": sender,
                "date": date,
                "snippet": snippet,
                "labels": msg["labelIds"],
                "id": message["id"]
            }
        )
    return formatted_messages
