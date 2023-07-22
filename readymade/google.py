import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import json
from email.mime.text import MIMEText
from requests import HTTPError
from src.gpt_function import gpt_function
import os

_SCOPES = [
        "https://mail.google.com/"
    ]


def init_services():
    """
    Initializes the Gmail service.
    :return:
    """

    creds = None
    # Import credentials or create new ones
    if os.path.exists('secret/token.json'):
        creds = Credentials.from_authorized_user_file('secret/token.json', _SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'secret/credentials.json', _SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('secret/token.json', 'w') as token:
            token.write(creds.to_json())

    if "service" not in st.session_state:
        st.session_state.service = build('gmail', 'v1', credentials=creds)
    return st.session_state.service

def get_email(service, id):
    msg = service.users().messages().get(userId="me", id=id).execute()
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
        body = msg["payload"]["parts"][0]["body"]["data"]
    else:
        body = body["data"]

    body = base64.urlsafe_b64decode(body).decode("utf-8")
    return {"subject": subject,
            "sender": sender,
            "date": date,
            "body": body,
            "labels": msg["labelIds"],
            "id": id
    }

@gpt_function
def get_user_email():
    """
    Useful for getting the email of the user you are talking to.
    """

    service = init_services()

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

    service = init_services()

    # Write markdown email
    message = MIMEText(body, "html")
    message["to"] = recipient_email
    message["subject"] = subject
    create_message = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}

    try:
        message = (service.users().messages().send(userId="me", body=create_message).execute())
        return {"outcome" : f'sent message to {message} Message Id: {message["id"]}'}
    except HTTPError as error:
        return {"outcome": f'An error occurred: {error}'}


@gpt_function
def search_email(query: str, max_results: int = 5):
    """
    Searches for emails that match the query.
    :param query: the query to search for. Use the same syntax as you would in gmail. Make it speicific.
    :param max_results: the maximum number of results to return, optional
    :return: a list of emails
    """

    print(query)

    service = init_services()

    results = service.users().messages().list(userId="me", q=query).execute()
    messages = results.get("messages", [])

    print(messages)

    if not messages:
        return {"outcome": "No messages found."}


    formatted_messages = {"messages": []}
    for message in messages[:max_results]:
        formatted_messages["messages"].append(
            get_email(service, message["id"])
        )

    print(formatted_messages)
    return formatted_messages


def get_calendar():
    """
    Useful for getting the calendar of the user you are talking to.
    """







