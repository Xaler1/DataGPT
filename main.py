import streamlit as st
import openai
import secret.keys as keys
from src.conversator import Conversator
from functions.weather import get_weather
from functions.google import send_email, get_user_email, search_email, get_email_by_id, reply_to_email
from functions.basic import get_basic_info
import traceback
import streamlit_js_eval as stjs

st.session_state.raw_geo = stjs.get_geolocation()

openai.api_key = keys.openai_key
gpt_weather = get_weather
gpt_send_email = send_email
gpt_get_user_info = get_user_email
gpt_search_email = search_email

st.title('GPT Assistant')
st.sidebar.button("Clear chat", on_click=lambda: st.session_state.conversator.reset())

if "conversator" not in st.session_state:
    st.session_state.conversator = Conversator([gpt_weather,
                                                gpt_send_email,
                                                gpt_get_user_info,
                                                gpt_search_email,
                                                get_basic_info,
                                                get_email_by_id,
                                                reply_to_email
                                                ])

with st.container():
    for message in st.session_state.conversator.get_messages():
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter your message"):
        with st.chat_message("user"):
            st.markdown(prompt)

            attempts = 0
            success = False
            while not success:
                attempts += 1
                if attempts > 4:
                    st.session_state.conversator.reset_to_last()
                    st.error("Something went wrong, please try again.")
                    st.stop()
                    break
                try:
                    response = st.session_state.conversator.process_msg(prompt)
                    success = True
                except Exception as e:
                    print("\n\n---------------------------------------------")
                    traceback.print_exc()
                    print("---------------------------------------------\n\n")


        with st.chat_message("assistant"):
            st.markdown(response)