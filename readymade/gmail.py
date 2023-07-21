import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import json
from email.mime.text import MIMEText
from requests import HTTPError
from src.gpt_function import gpt_function


@gpt_function
def send_email(to: str, subject: str, body: str):
    """
    Useful for sending an email from a gmail account.

    :param to: the email of the recipient
    :param subject: the subject of the email
    :param body: the body of the email
    """

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.readonly"
    ]

    if "service" not in st.session_state:
        flow = InstalledAppFlow.from_client_secrets_file('secret/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        st.session_state.service = build('gmail', 'v1', credentials=creds)

    service = st.session_state.service

    message = MIMEText(body, "html")
    message['to'] = to
    message['subject'] = subject
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    try:
        message = (service.users().messages().send(userId="me", body=create_message).execute())
        return {"outcome" : f'sent message to {message} Message Id: {message["id"]}'}
    except HTTPError as error:
        return {"outcome": f'An error occurred: {error}'}


