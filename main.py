import streamlit as st
import openai
import secret.keys as keys
from src.conversator import Conversator
from readymade.weather import get_current_weather
from readymade.gmail import send_email

openai.api_key = keys.openai_key
gpt_weather = get_current_weather
gpt_send_email = send_email

st.title('GPT Assistant')
st.sidebar.button("Clear chat", on_click=lambda: st.session_state.conversator.reset())

if "conversator" not in st.session_state:
    st.session_state.conversator = Conversator([gpt_weather, send_email])

with st.container():
    for message in st.session_state.conversator.get_messages():
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter your message"):
        with st.chat_message("user"):
            st.markdown(prompt)
            response = st.session_state.conversator.process_msg(prompt)

        with st.chat_message("assistant"):
            st.markdown(response)