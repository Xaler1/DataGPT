import streamlit as st
import openai
import secret.keys as keys
from src.conversator import Conversator
from functions.weather import get_weather
from functions.news import get_news_headlines, get_full_article
from functions.gmaps import search_place, get_place_details
from functions.basic import get_basic_info
from data.storage import manual_write_data, get_data_details
from data.manipulation import analyze_data
from data.plotting import plot_data
import traceback
import streamlit_js_eval as stjs


class Chat:
    def __init__(self):
        pass

    def run(self):
        st.session_state.raw_geo = stjs.get_geolocation()
        openai.api_key = keys.openai_key

        # Initialize the conversator and save it to the session state
        if "conversator" not in st.session_state:
            st.session_state.conversator = Conversator([get_weather,
                                                        get_basic_info,
                                                        #get_user_email,
                                                        #send_email, search_email, get_email_by_id, reply_to_email,
                                                        get_news_headlines, get_full_article,
                                                        # search_places, find_nearby,
                                                        search_place, get_place_details,
                                                        #get_cik, get_company_info, get_company_filings, get_full_filing,
                                                        plot_data,
                                                        manual_write_data, get_data_details,
                                                        analyze_data
                                                        ])

        with st.sidebar.expander("functions", expanded=False):
            for function in st.session_state.conversator.all_functions:
                st.checkbox(function.name, value=True)

        with st.container():
            for message in st.session_state["messages"]:
                if message["role"] == "plot":
                    st.pyplot(message["content"], use_container_width=True)
                if message["role"] == "image":
                    st.image(message["content"])
                else:
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